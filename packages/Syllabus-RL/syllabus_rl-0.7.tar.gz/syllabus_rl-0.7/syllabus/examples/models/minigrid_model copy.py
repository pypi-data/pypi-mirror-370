
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


def init(module, weight_init, bias_init, gain=1):
    weight_init(module.weight.data, gain=gain)
    bias_init(module.bias.data)
    return module


def init_(m): return init(m, nn.init.orthogonal_, lambda x: nn.init.
                          constant_(x, 0))


def init_relu_(m): return init(m, nn.init.orthogonal_, lambda x: nn.init.
                               constant_(x, 0), nn.init.calculate_gain('relu'))


def init_tanh_(m): return init(m, nn.init.orthogonal_, lambda x: nn.init.
                               constant_(x, 0), np.sqrt(2))


def apply_init_(modules, gain=None):
    """
    Initialize NN modules
    """
    for m in modules:
        if isinstance(m, nn.Conv2d):
            if gain:
                nn.init.xavier_uniform_(m.weight, gain=gain)
            else:
                nn.init.xavier_uniform_(m.weight)
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)
        elif isinstance(m, (nn.BatchNorm2d, nn.GroupNorm)):
            nn.init.constant_(m.weight, 1)
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)


class Flatten(nn.Module):
    """
    Flatten a tensor
    """

    def forward(self, x):
        return x.reshape(x.size(0), -1)


class FixedCategorical(torch.distributions.Categorical):
    """
    Categorical distribution object
    """

    def sample(self):
        return super().sample().unsqueeze(-1)

    def log_probs(self, actions):
        return (
            super()
            .log_prob(actions.squeeze(-1))
            .view(actions.size(0), -1)
            .sum(-1)
            .unsqueeze(-1)
        )

    def mode(self):
        return self.probs.argmax(dim=-1, keepdim=True)


class Categorical(nn.Module):
    """
    Categorical distribution (NN module)
    """

    def __init__(self, num_inputs, num_outputs):
        super(Categorical, self).__init__()

        def init_(m): return init(
            m,
            nn.init.orthogonal_,
            lambda x: nn.init.constant_(x, 0),
            gain=0.01)

        self.linear = init_(nn.Linear(num_inputs, num_outputs))

    def forward(self, x):
        x = self.linear(x)
        return FixedCategorical(logits=x)


class DeviceAwareModule(nn.Module):
    @property
    def device(self):
        return next(self.parameters()).device


class Conv2d_tf(nn.Conv2d):
    """
    Conv2d with the padding behavior from TF
    """

    def __init__(self, *args, **kwargs):
        super(Conv2d_tf, self).__init__(*args, **kwargs)
        self.padding = kwargs.get("padding", "same")

    def _compute_padding(self, input, dim):
        input_size = input.size(dim + 2)
        filter_size = self.weight.size(dim + 2)
        effective_filter_size = (filter_size - 1) * self.dilation[dim] + 1
        out_size = (input_size + self.stride[dim] - 1) // self.stride[dim]
        total_padding = max(
            0, (out_size - 1) * self.stride[dim] + effective_filter_size - input_size
        )
        additional_padding = int(total_padding % 2 != 0)

        return additional_padding, total_padding

    def forward(self, input):
        if self.padding == "valid":
            return F.conv2d(
                input,
                self.weight,
                self.bias,
                self.stride,
                padding=0,
                dilation=self.dilation,
                groups=self.groups,
            )
        rows_odd, padding_rows = self._compute_padding(input, dim=0)
        cols_odd, padding_cols = self._compute_padding(input, dim=1)
        if rows_odd or cols_odd:
            input = F.pad(input, [0, cols_odd, 0, rows_odd])

        return F.conv2d(
            input,
            self.weight,
            self.bias,
            self.stride,
            padding=(padding_rows // 2, padding_cols // 2),
            dilation=self.dilation,
            groups=self.groups,
        )


class RNN(nn.Module):
    """
    Actor-Critic network (base class)
    """

    def __init__(self, input_size, hidden_size=128, arch='lstm'):
        super().__init__()

        self.arch = arch
        self.is_lstm = arch == 'lstm'

        self._hidden_size = hidden_size
        if arch == 'gru':
            self.rnn = nn.GRU(input_size, hidden_size)
        elif arch == 'lstm':
            self.rnn = nn.LSTM(input_size, hidden_size)
        else:
            raise ValueError(f'Unsupported RNN architecture {arch}.')

        for name, param in self.rnn.named_parameters():
            if 'bias' in name:
                nn.init.constant_(param, 0)
            elif 'weight' in name:
                nn.init.orthogonal_(param)

    @property
    def recurrent_hidden_state_size(self):
        return self._hidden_size

    @property
    def output_size(self):
        return self._hidden_size

    def forward(self, x, hxs, masks):
        if self.is_lstm:
            # Since nn.LSTM defaults to all zero states if passed None state
            hidden_batch_size = x.size(0) if hxs is None else hxs[0].size(0)
        else:
            hidden_batch_size = hxs.size(0)

        if x.size(0) == hidden_batch_size:
            masked_hxs = tuple((h*masks).unsqueeze(0) for h in hxs) if self.is_lstm \
                else (hxs*masks).unsqueeze(0)

            x, hxs = self.rnn(x.unsqueeze(0), masked_hxs)
            x = x.squeeze(0)

            hxs = tuple(h.squeeze(0) for h in hxs) if self.is_lstm else hxs.squeeze(0)
        else:
            # x is a (T, N, -1) tensor that has been flatten to (T * N, -1)
            N = hxs[0].size(0) if self.is_lstm else hxs.size(0)
            T = int(x.size(0) / N)

            # unflatten
            x = x.view(T, N, x.size(1))

            # Same deal with masks
            masks = masks.view(T, N)

            # Let's figure out which steps in the sequence have a zero for any agent
            # We will always assume t=0 has a zero in it as that makes the logic cleaner
            has_zeros = ((masks[1:] == 0.0)
                         .any(dim=-1)
                         .nonzero()
                         .squeeze()
                         .cpu())

            # +1 to correct the masks[1:]
            if has_zeros.dim() == 0:
                # Deal with scalar
                has_zeros = [has_zeros.item() + 1]
            else:
                has_zeros = (has_zeros + 1).numpy().tolist()

            # add t=0 and t=T to the list
            has_zeros = [0] + has_zeros + [T]

            hxs = (h.unsqueeze(0) for h in hxs) if self.is_lstm else hxs.unsqueeze(0)
            outputs = []
            for i in range(len(has_zeros) - 1):
                # We can now process steps that don't have any zeros in masks together!
                # This is much faster
                start_idx = has_zeros[i]
                end_idx = has_zeros[i + 1]

                masked_hxs = tuple(h*masks[start_idx].view(1, -1, 1) for h in hxs) if self.is_lstm \
                    else hxs*masks[start_idx].view(1, -1, 1)
                rnn_scores, hxs = self.rnn(
                    x[start_idx:end_idx],
                    masked_hxs)

                outputs.append(rnn_scores)

            # assert len(outputs) == T
            # x is a (T, N, -1) tensor
            x = torch.cat(outputs, dim=0)
            # flatten
            x = x.view(T * N, -1)
            hxs = tuple(h.squeeze(0) for h in hxs) if self.is_lstm else hxs.squeeze(0)

        return x, hxs


def one_hot(dim, inputs, device='cpu'):
    one_hot = torch.nn.functional.one_hot(inputs.long(), dim).squeeze(1).float()
    return one_hot


def make_fc_layers_with_hidden_sizes(sizes, input_size):
    fc_layers = []
    for i, layer_size in enumerate(sizes[:-1]):
        input_size = input_size if i == 0 else sizes[0]
        output_size = sizes[i+1]
        fc_layers.append(init_tanh_(nn.Linear(input_size, output_size)))
        fc_layers.append(nn.Tanh())

    return nn.Sequential(
        *fc_layers
    )


class MinigridAgent(nn.Module):
    """
    Actor-Critic module 
    """

    def __init__(self,
                 observation_shape,
                 num_actions,
                 actor_fc_layers=(32, 32),
                 value_fc_layers=(32, 32),
                 conv_filters=16,
                 conv_kernel_size=3,
                 scalar_fc=5,
                 scalar_dim=4,
                 random_z_dim=0,
                 xy_dim=0,
                 recurrent_arch='lstm',
                 recurrent_hidden_size=256,
                 random=False):
        super(MinigridAgent, self).__init__()

        self.random = random

        # Image embeddings
        obs_shape = observation_shape
        m = obs_shape[-2]  # x input dim
        n = obs_shape[-1]  # y input dim
        c = obs_shape[-3]  # channel input dim

        self.image_conv = nn.Sequential(
            Conv2d_tf(3, conv_filters, kernel_size=conv_kernel_size, stride=1, padding='valid'),
            nn.Flatten(),
            nn.ReLU()
        )
        self.image_embedding_size = (n - conv_kernel_size + 1) * (m - conv_kernel_size + 1) * conv_filters
        self.preprocessed_input_size = self.image_embedding_size

        # x, y positional embeddings
        self.xy_embed = None
        self.xy_dim = xy_dim
        if xy_dim:
            self.preprocessed_input_size += 2 * xy_dim

        # Scalar embedding
        self.scalar_embed = None
        self.scalar_dim = scalar_dim
        if scalar_dim:
            self.scalar_embed = nn.Linear(scalar_dim, scalar_fc)
            self.preprocessed_input_size += scalar_fc

        self.preprocessed_input_size += random_z_dim
        self.base_output_size = self.preprocessed_input_size

        # RNN
        self.rnn = None
        if recurrent_arch:
            self.rnn = RNN(
                input_size=self.preprocessed_input_size,
                hidden_size=recurrent_hidden_size,
                arch=recurrent_arch)
            self.base_output_size = recurrent_hidden_size

        # Policy head
        self.actor = nn.Sequential(
            make_fc_layers_with_hidden_sizes(actor_fc_layers, input_size=self.base_output_size),
            Categorical(actor_fc_layers[-1], num_actions)
        )

        # Value head
        self.critic = nn.Sequential(
            make_fc_layers_with_hidden_sizes(value_fc_layers, input_size=self.base_output_size),
            init_(nn.Linear(value_fc_layers[-1], 1))
        )

        apply_init_(self.modules())

        self.train()

    @property
    def recurrent_hidden_state_size(self):
        # """Size of rnn_hx."""
        if self.rnn is not None:
            return self.rnn.recurrent_hidden_state_size
        else:
            return 0

    def _forward_base(self, inputs, rnn_hxs, masks):
        # Unpack input key values
        image = inputs.get('image')
        scalar = inputs.get('direction')

        in_image = self.image_conv(image)
        in_x = torch.tensor([], device=self.device)
        in_y = torch.tensor([], device=self.device)
        in_z = torch.tensor([], device=self.device)
        in_scalar = one_hot(self.scalar_dim, scalar).to(self.device)
        in_scalar = self.scalar_embed(in_scalar)
        in_embedded = torch.cat((in_image, in_x, in_y, in_scalar, in_z), dim=-1)

        core_features, rnn_hxs = self.rnn(in_embedded, rnn_hxs, masks)
        return core_features, rnn_hxs

    def get_value(self, inputs, rnn_hxs, masks):
        core_features, rnn_hxs = self._forward_base(inputs, rnn_hxs, masks)
        return self.critic(core_features)

    def get_action_and_value(self, inputs, rnn_hxs, dones, action=None, deterministic=False):
        masks = torch.FloatTensor(1 - dones.cpu()).cuda()
        core_features, rnn_hxs = self._forward_base(inputs, rnn_hxs, masks)
        dist = self.actor(core_features)
        value = self.critic(core_features)
        if action is None:
            action = dist.mode() if deterministic else dist.sample()
        action_log_probs = dist.log_probs(action)
        dist_entropy = dist.entropy().mean()

        return torch.squeeze(action), action_log_probs, dist_entropy, value, rnn_hxs
