# -*- coding: utf-8 -*-
"""
pycol._simulate

Created on 09.01.2022

@author: Patrick Mueller

Classes and methods for the 'simulate' module using the Python/C++ interface.
"""

import numpy as np
from matplotlib import cm
import matplotlib.pyplot as plt

from .types import *
from . import tools
from . import physics as ph
from .cpp.cpp import *


def sr_generate_y(denominator: np.ndarray, f_theta: np.ndarray, f_phi: np.ndarray,
                  counts: np.ndarray, shape: np.ndarray):
    """
    :param denominator:
    :param f_theta:
    :param f_phi:
    :param counts:
    :param shape:
    :return:
    """
    y = np.zeros((shape[0] * shape[1], ), dtype=float)  # Allocate memory.
    denominator_p = denominator.ctypes.data_as(c_complex_p)  # Get all pointers to the first elements of the arrays.
    f_theta_p = f_theta.ctypes.data_as(c_complex_p)
    f_phi_p = f_phi.ctypes.data_as(c_complex_p)
    counts_p = counts.ctypes.data_as(c_int_p)
    shape_p = shape.ctypes.data_as(c_int_p)
    y_p = y.ctypes.data_as(c_double_p)
    dll.sr_generate_y(denominator_p, f_theta_p, f_phi_p, counts_p, shape_p, y_p)  # Modify y "in-place" with C++.
    return y


def _process_q_axis(q_axis: array_like) -> ndarray:
    """
    Preprocess the quantization axis.

    :param q_axis: The quantization axis. Must be an integer in {0, 1, 2} or a 3d-vector.
    :returns: The quantization axis as a 3d-vector.
    """
    q_axis = np.asarray(q_axis, dtype=float)
    if not q_axis.shape:
        if q_axis % 1 != 0:
            raise ValueError('q_axis must be an integer or a 3d-vector.')
        elif int(q_axis) not in {0, 1, 2}:
            raise ValueError('q_axis must be in {0, 1, 2}.')
        else:
            q_axis = tools.unit_vector(int(q_axis), 3)
    elif q_axis.shape != (3,):
        raise ValueError('q_axis must be an integer or a 3d-vector.')
    return q_axis


class Polarization:
    """
    Class representing a polarization state of light. The property 'x' holds the polarization in cartesian coordinates.
    The property 'q' holds the polarization in spherical coordinates ( sigma-, pi, sigma+ )
    with respect to the chosen quantization axis.
    """

    def __init__(self, vec: array_iter = None, q_axis: array_like = 2, vec_as_q: bool = True, instance=None):
        """
        :param vec: The polarization vector. I.e. the amplitude of the electromagnetic wave. So to specify, e.g.,
         1/3 of pi and 2/3 sigma+ light for a given 'q_axis', vec must be ( 0, sqrt(1/3), sqrt(2/3) ).
         The default is linear polarization in z-direction, such that x = (0, 0, 1) and q = (0, 1, 0).
        :param q_axis: The quantization axis. Must be an integer in {0, 1, 2} or a 3d-vector. The default is 2 (z-axis).
        :param vec_as_q: Whether 'vec' is given as ( sigma-, pi, sigma+ ) (True) or in cartesian coordinates (False).
        :param instance: A pointer to an existing Polarization instance.
         If this is specified, the other parameters are omitted.
        """
        self.instance = instance
        if self.instance is None:
            self.instance = dll.polarization_construct()

            if vec is None:
                vec = tools.unit_vector(1, 3, dtype=complex)
            vec = np.asarray(vec, dtype=complex)
            if vec.shape != (3,):
                raise ValueError('vec must be a 3d-vector.')

            q_axis = _process_q_axis(q_axis)
            dll.polarization_init(self.instance, vec, q_axis, vec_as_q)

    def __del__(self):
        dll.polarization_destruct(self.instance)

    def def_q_axis(self, q_axis: array_like = 2, q_fixed: bool = False):
        """
        Defines the quantization axis. This changes either 'x' or 'q', depending on 'q_fixed'.

        :param q_axis: The quantization axis. Must be an integer in {0, 1, 2} or a 3d-vector. The default is 2 (z-axis).
        :param q_fixed: Whether 'q' should stay the same with the new quantization axis (True) or 'x' (False).
        """
        q_axis = _process_q_axis(q_axis)
        dll.polarization_def_q_axis(self.instance, q_axis, q_fixed)

    @property
    def q_axis(self) -> ndarray:
        """
        :returns: The complex polarization in spherical coordinates ( sigma-, pi, sigma+ ).
        """
        return dll.polarization_get_q_axis(self.instance)

    @property
    def x(self) -> ndarray:
        """
        :returns: The complex polarization in cartesian coordinates ( x, y, z ).
        """
        return dll.polarization_get_x(self.instance)

    @property
    def q(self) -> ndarray:
        """
        :returns: The complex polarization in spherical coordinates ( sigma-, pi, sigma+ ).
        """
        return dll.polarization_get_q(self.instance)


class Laser:
    """
    Class representing a laser.
    """

    def __init__(self, freq: scalar, intensity: scalar = 1., polarization: Polarization = None,
                 k: array_like = None, instance=None):
        """
        :param freq: The frequency of the laser (MHz).
        :param intensity: The intensity of the laser (uW / mm**2 = W / m**2).
        :param polarization: The polarization of the laser.
        :param instance: A pointer to an existing Laser instance.
         If this is specified, the other parameters are omitted.
        """
        self.instance = instance
        if self.instance is None:
            self.instance = dll.laser_construct()
            self._polarization = polarization
            if self.polarization is None:
                self._polarization = Polarization()
            dll.laser_init(self.instance, c_double(freq), c_double(intensity), polarization.instance)
            if k is None:
                k = tools.unit_vector(0, 3)
            self.k = k
        else:
            self._polarization = Polarization(instance=dll.laser_get_polarization(self.instance))

    def __del__(self):
        dll.laser_destruct(self.instance)

    @property
    def freq(self):
        """
        :returns: The frequency of the laser.
        """
        return dll.laser_get_freq(self.instance)

    @freq.setter
    def freq(self, value: scalar):
        """
        :param value: The new frequency of the laser.
        :returns: None.
        """
        dll.laser_set_freq(self.instance, c_double(value))

    @property
    def intensity(self):
        """
        :returns: The intensity of the laser.
        """
        return dll.laser_get_intensity(self.instance)

    @intensity.setter
    def intensity(self, value: scalar):
        """
        :param value: The new intensity of the laser.
        :returns: None.
        """
        dll.laser_set_intensity(self.instance, c_double(value))

    @property
    def polarization(self):
        """
        :returns: The polarization of the laser.
        """
        return self._polarization

    @polarization.setter
    def polarization(self, value: Polarization):
        """
        :param value: The new polarization of the laser.
        :return: None.
        """
        self._polarization = value
        dll.laser_set_polarization(self.instance, value.instance)

    @property
    def k(self):
        """
        :returns: The direction of the laser. The default direction is ( 1, 0, 0 ).
        """
        return dll.laser_get_k(self.instance)

    @k.setter
    def k(self, value: array_like):
        """
        :param value: The new direction of the laser.
        :return: None.
        """
        _value = np.asarray(value, dtype=float)
        if _value.size != 3:
            raise ValueError('Interaction.k must be a 3d-vector, but has shape {}.'.format(_value.shape))
        dll.laser_set_k(self.instance, _value.flatten())


def _process_hyper_const(hyper_const: array_like) -> ndarray:
    """
    Preprocess the hyperfine-structure constants.

    :param hyper_const: The hyperfine-structure constants. Currently, constants up to the electric quadrupole order are
     supported (A, B). If 'hyper_const' is a scalar, it is assumed to be the constant A and the other orders are 0.
    :returns: The hyperfine-structure constants as a 3d-vector.
    """
    if hyper_const is None or not hyper_const:
        hyper_const = [0., 0., 0.]
    elif not np.asarray(hyper_const, dtype=float).shape:
        hyper_const = [float(hyper_const), 0., 0.]
    hyper_const = list(hyper_const)
    while len(hyper_const) < 3:
        hyper_const.append(0.)
    return np.asarray(hyper_const, dtype=float)[:3]


# noinspection PyPep8Naming
class Environment:
    """
    Class representing an electromagnetic environment.
    """

    def __init__(self, E: array_like = None, B: array_like = None, instance=None):
        self.instance = instance
        if self.instance is None:
            self.instance = dll.environment_construct()
            self.E = E
            self.B = B

    def __del__(self):
        dll.environment_destruct(self.instance)

    @property
    def E(self):
        return dll.environment_get_E(self.instance) * dll.environment_get_e_E(self.instance)
    
    @E.setter
    def E(self, value: array_like):
        if value is None:
            dll.environment_set_E(self.instance, np.asarray([1, 0, 0], dtype=float))
            dll.environment_set_E_double(self.instance, c_double(0.))
        else:
            value = np.asarray(value, dtype=float)
            if not value.shape:
                dll.environment_set_E_double(self.instance, value)
            elif value.shape == (3, ):
                dll.environment_set_E(self.instance, value)
            else:
                raise ValueError('E must be a scalar, 3d-vector or None, but has shape {}'.format(value.shape))

    @property
    def B(self):
        return dll.environment_get_B(self.instance) * dll.environment_get_e_B(self.instance)
    
    @B.setter
    def B(self, value: array_like):
        if value is None:
            dll.environment_set_B(self.instance, np.array([0, 0, 1], dtype=float))
            dll.environment_set_B_double(self.instance, c_double(0.))
        else:
            value = np.asarray(value, dtype=float)
            if not value.shape:
                dll.environment_set_B_double(self.instance, value)
            elif value.shape == (3, ):
                dll.environment_set_B(self.instance, value)
            else:
                raise ValueError('B must be a scalar, 3d-vector or None, but has shape {}'.format(value.shape))


class State:
    """
    Class representing an atomic quantum state :math:`|(\\mathrm{label})SLJIFm\\rangle`.
    """
    def __init__(self, freq_j: scalar, s: scalar, l: scalar, j: scalar, i: scalar, f: scalar, m: scalar,
                 hyper_const: array_like = None, g: scalar = 0, label: str = None, instance=None):
        """
        :param freq_j: The energetic position of the state without the hyperfine structure or the environment (MHz).
        :param s: The electron spin quantum number S.
        :param l: The electronic angular momentum quantum number L.
        :param j: The electronic total angular momentum quantum number J.
        :param i: The nuclear spin quantum number I.
        :param f: The total angular momentum quantum number F.
        :param m: The B-field-axis component quantum number m of the total angular momentum.
        :param hyper_const: The hyperfine-structure constants. Currently, constants up to the electric quadrupole order
         are supported (A, B). If 'hyper_const' is a scalar, it is assumed to be the constant A
         and the other orders are 0 (MHz).
        :param g: The nuclear g-factor.
        :param label: The label of the state. The label is used to link states via decay maps.
        :param instance: A pointer to an existing State instance.
         If this is specified, the other parameters are omitted.
        """
        self.instance = instance
        if self.instance is None:
            tools.check_half_integer(s, l, j, i, f, m)
            hyper_const = _process_hyper_const(hyper_const)
            if label is None:
                label = '{}({}, {}, {})'.format(int(np.around(freq_j, decimals=0)), s, l, j)
            self.instance = dll.state_construct()
            dll.state_init(self.instance, c_double(freq_j), c_double(s), c_double(l), c_double(j), c_double(i),
                           c_double(f), c_double(m), hyper_const, c_double(g), c_char_p(bytes(label, 'utf-8')))

    def __del__(self):
        dll.state_destruct(self.instance)

    def __repr__(self):
        return '{}({})'.format(self.label, ('{}, ' * 6)[:-2]) \
            .format(*[tools.half_integer_to_str(qn, '/') for qn in [self.s, self.l, self.j, self.i, self.f, self.m]])

    def update(self, environment: Environment = None):
        """
        Update the shifted frequency of the state.

        :returns: None.
        """
        if environment is None:
            dll.state_update(self.instance)
        else:
            dll.state_update_env(self.instance, environment.instance)

    def get_shift(self):
        """
        :returns: The difference between the shifted frequency of the hyperfine-structure
         and the frequency of the fine-structure state.
        """
        return dll.state_get_shift(self.instance)

    @property
    def freq_j(self):
        """
        :returns: The frequency of the fine-structure state.
        """
        return dll.state_get_freq_j(self.instance)

    @freq_j.setter
    def freq_j(self, value: scalar):
        dll.state_set_freq_j(self.instance, c_double(value))

    @property
    def freq(self):
        """
        :returns: The shifted frequency of the hyperfine-structure state.
        """
        return dll.state_get_freq(self.instance)

    @property
    def s(self):
        """
        :returns: The electron spin quantum number S.
        """
        return dll.state_get_s(self.instance)

    @property
    def l(self):
        """
        :returns: The electronic angular momentum quantum number L.
        """
        return dll.state_get_l(self.instance)

    @property
    def j(self):
        """
        :returns: The electronic total angular momentum quantum number J.
        """
        return dll.state_get_j(self.instance)

    @property
    def i(self):
        """
        :returns: The nuclear spin quantum number I.
        """
        return dll.state_get_i(self.instance)

    @property
    def f(self):
        """
        :returns: The total angular momentum quantum number F.
        """
        return dll.state_get_f(self.instance)

    @property
    def m(self):
        """
        :returns: The B-field-axis component quantum number m of the total angular momentum.
        """
        return dll.state_get_m(self.instance)

    @property
    def hyper_const(self):
        """
        :returns: The hyperfine-structure constants as a 3d-vector.
        """
        return dll.state_get_hyper_const(self.instance)

    @hyper_const.setter
    def hyper_const(self, value: array_like):
        """
        :param value: The new hyperfine-structure constants. Currently, constants up to the electric quadrupole order
         are supported (A, B). If 'hyper_const' is a scalar, it is assumed to be the constant A
         and the other orders are 0 (MHz).
        :returns: None.
        """
        value = _process_hyper_const(value)
        dll.state_get_hyper_const(self.instance, value)

    @property
    def g(self):
        """
        :returns: The nuclear g-factor.
        """
        return dll.state_get_g(self.instance)

    @g.setter
    def g(self, value: scalar):
        """
        :param value: The new nuclear g-factor.
        :returns: None.
        """
        dll.state_set_g(self.instance, c_double(value))

    @property
    def label(self):
        """
        :returns: The label of the state. The label is used to link states via decay maps.
        """
        return dll.state_get_label(self.instance).decode('utf-8')

    @label.setter
    def label(self, value: str):
        """
        :param value: The label of the state. The label is used to link states via decay maps.
        :returns: None.
        """
        dll.state_set_label(self.instance, c_char_p(bytes(value, 'utf-8')))


def construct_electronic_state(freq_0: scalar, s: scalar, l: scalar, j: scalar, i: scalar = 0,
                               hyper_const: Iterable[scalar] = None, g: scalar = 0, label: str = None):
    """
    Creates all substates of a fine-structure state using a common label.

    :param freq_0: The energetic position of the state without the hyperfine structure or the magnetic field (MHz).
    :param s: The electron spin quantum number S.
    :param l: The electronic angular momentum quantum number L.
    :param j: The electronic total angular momentum quantum number J.
    :param i: The nuclear spin quantum number I.
    :param hyper_const: The hyperfine-structure constants. Currently, constants up to the electric quadrupole order are
     supported (A, B). If 'hyper_const' is a scalar, it is assumed to be the constant A and the other orders are 0.
    :param g: The nuclear g-factor.
    :param label: The label of the states. The labels are used to link states via decay maps.
    :returns: A list of the created states.
    """
    f = ph.get_f(i, j)
    m = [ph.get_m(_f) for _f in f]
    fm = [(_f, _m) for _f, m_f in zip(f, m) for _m in m_f]
    return [State(freq_0, s, l, j, i, _f, _m, hyper_const=hyper_const, g=g, label=label) for (_f, _m) in fm]


def construct_hyperfine_state(freq_0: scalar, s: scalar, l: scalar, j: scalar, i: scalar, f: scalar,
                              hyper_const: Iterable[scalar] = None, g: scalar = 0, label: str = None):
    """
    Creates all substates of a fine-structure state using a common label.

    :param freq_0: The energetic position of the state without the hyperfine structure or the magnetic field (MHz).
    :param s: The electron spin quantum number S.
    :param l: The electronic angular momentum quantum number L.
    :param j: The electronic total angular momentum quantum number J.
    :param i: The nuclear spin quantum number I.
    :param f: The hyperfine structure total angular momentum quantum number F.
    :param hyper_const: The hyperfine-structure constants. Currently, constants up to the electric quadrupole order are
     supported (A, B). If 'hyper_const' is a scalar, it is assumed to be the constant A and the other orders are 0.
    :param g: The nuclear g-factor.
    :param label: The label of the states. The labels are used to link states via decay maps.
    :returns: A list of the created states.
    """
    m = ph.get_m(f)
    return [State(freq_0, s, l, j, i, f, _m, hyper_const=hyper_const, g=g, label=label) for _m in m]


class DecayMap:
    """
    Class linking sets of atomic states via Einstein-A coefficients.
    """
    def __init__(self, labels: Iterable[tuple] = None, a: Iterable[scalar] = None, instance=None):
        """
        :param labels: An iterable of label pairs, corresponding to atomic states which get connected.
        :param a: An Iterable of Einstein-A coefficients.
        :param instance: A pointer to an existing DecayMap instance.
         If this is specified, the other parameters are omitted.
        """
        self.instance = instance

        if self.instance is None:
            self.instance = dll.decaymap_construct()
            if labels is None:
                labels = []
            if a is None:
                a = []
            self._labels = list(labels)
            for (s0, s1), _a in zip(self._labels, a):
                dll.decaymap_add_decay(self.instance, c_char_p(bytes(s0, 'utf-8')), c_char_p(bytes(s1, 'utf-8')),
                                       c_double(float(_a)))
        else:
            self._labels = self._get_labels()

    def __del__(self):
        dll.decaymap_destruct(self.instance)

    def _get_labels(self):
        """
        :returns: The labels used in the C++ class.
        """
        return [(dll.decaymap_get_label(self.instance, 0, i).decode('utf-8'),
                 dll.decaymap_get_label(self.instance, 1, i).decode('utf-8')) for i in range(self.size)]

    @property
    def labels(self):
        """
        :returns: The list of label pairs, corresponding to atomic states which get connected.
        """
        return self._labels

    @property
    def a(self):
        """
        :returns: The list of Einstein-A coefficients.
        """
        vector_d_p = np.ctypeslib.ndpointer(dtype=float, shape=(self.size, ))
        set_restype(dll.decaymap_get_a, vector_d_p)
        return dll.decaymap_get_a(self.instance).tolist()

    @property
    def size(self):
        """
        :returns: The number of linked sets of atomic states.
        """
        return dll.decaymap_get_size(self.instance)


def _gen_label_map(atom):
    """
    :param atom: The atom.
    :returns: A dictionary with state labels as keys
     and an array of the indices of the states with the labels as values.
    """
    if isinstance(atom, int):
        return {'States 0 - {}'.format(atom): np.arange(atom, dtype=int)}
    all_labels = [s.label for s in atom]
    labels = []
    for s in all_labels:
        if s not in labels:
            labels.append(s)
    label_map = {s: np.array([i for i, _s in enumerate(all_labels) if _s == s]) for s in labels}
    return label_map


class Atom:
    """
    Class representing an Atom and its inner structure.
    """
    def __init__(self, states: Iterable[State] = None, decay_map: DecayMap = None, mass: scalar = 0, instance=None):
        """
        :param states: The states of the atom.
        :param decay_map: The decay map which connects the atomic states.
        :param mass: The mass of the atom.
        :param instance: A pointer to an existing Atom instance.
         If this is specified, the other parameters are omitted.
        """
        self.instance = instance

        if self.instance is None:
            self.instance = dll.atom_construct()
            if states is None:
                states = []
            if decay_map is None:
                decay_map = DecayMap()
            self.states = list(states)
            self.decay_map = decay_map
            self.mass = mass
            self.label_map = None
            self.update()
        else:
            self._states = None

    def __del__(self):
        dll.atom_destruct(self.instance)

    def __iter__(self):
        for state in self.states:
            yield state

    def __getitem__(self, key: int):
        return self.states[key]

    def update(self):
        """
        Update the atom.

        :returns: None.
        """
        dll.atom_update(self.instance)
        self.label_map = _gen_label_map(self)

    @property
    def states(self):
        """
        :returns: The states of the atom.
        """
        return self._states

    @states.setter
    def states(self, value: Iterable[State]):
        """
        :param value: The new states of the atom.
        :returns: None.
        """
        dll.atom_clear_states(self.instance)
        self._states = list(value)
        for s in self._states:
            dll.atom_add_state(self.instance, s.instance)

    @property
    def decay_map(self):
        """
        :returns: The decay map which connects the atomic states.
        """
        return self._decay_map

    @decay_map.setter
    def decay_map(self, value: DecayMap):
        """
        :param value: The new decay map which connects the atomic states.
        :returns: None.
        """
        self._decay_map = value
        if self._decay_map is None:
            self._decay_map = DecayMap()
        dll.atom_set_decay_map(self.instance, value.instance)

    @property
    def mass(self):
        """
        :returns: The mass of the atom.
        """
        return dll.atom_get_mass(self.instance)

    @mass.setter
    def mass(self, value: scalar):
        """
        :param value: The new mass of the atom.
        :returns: None.
        """
        dll.atom_set_mass(self.instance, c_double(value))

    @property
    def size(self):
        """
        :returns: The number of states of the atom.
        """
        return dll.atom_get_size(self.instance)

    @property
    def gs(self) -> ndarray:
        """
        :returns: The indices of the ground states.
        """
        vector_i_p = np.ctypeslib.ndpointer(dtype=c_size_t, shape=(dll.atom_get_gs_size(self.instance), ))
        set_restype(dll.atom_get_gs, vector_i_p)
        return dll.atom_get_gs(self.instance)

    @property
    def dipoles(self):
        """
        :returns: The dipole strengths between the atomic states in the 3 basis-components
         of the spherical vector basis ( sigma-, pi, sigma+ ). This can be used to calculate Rabi-frequencies by
         multiplying it with the square-root of a laser intensity in the corresponding polarization.
         The resulting array has shape (3, size, size).
        """
        return np.array([np.ctypeslib.as_array(dll.atom_get_m_dipole(self.instance, c_size_t(i)),
                                               (self.size, self.size)).T for i in range(3)])

    @property
    def l0(self):
        a = dll.atom_get_L0(self.instance)
        return np.ctypeslib.as_array(a, (self.size, self.size)).T

    @property
    def l1(self):
        a = dll.atom_get_L1(self.instance)
        return np.ctypeslib.as_array(a, (self.size, self.size)).T

    def get_y0(self, ground_state_labels: Union[Iterable[str], str] = None) -> np.ndarray:
        """
        :param ground_state_labels: An Iterable of labels belonging to ground states.
        :returns: The initial population of the atom.
        """
        y0 = np.zeros(self.size)
        if ground_state_labels is None:
            ground_state_labels = [self.states[0].label]
        indices = np.array([i for i, state in enumerate(self) if state.label in ground_state_labels])
        y0[indices] = 1 / indices.size
        return y0

    def plot(self, indices: array_like = None, draw_bounds: bool = False, show: bool = True):
        """
        Plot a term scheme of the atom.

        :param indices: The indices of the states to be drawn. If None, all states are drawn.
        :param draw_bounds: Whether to draw the upper vertical bounds of the states.
        :param show: Whether to show the plot.
        :returns: The x and y positions of the states as well as the distance constant d.
        """
        if indices is None:
            indices = np.argsort([state.freq for state in self.states])
        d = 2
        y_i = 0
        y_dict = {}
        m_max = max(s.m for s in self.states)
        ret_x = {}
        ret_y = {}
        for i in indices:
            s = self.states[i]
            key = (s.label, s.s, s.l, s.j, s.i, s.f)
            if key not in y_dict.keys():
                if key[:-1] not in [key_1[:-1] for key_1 in y_dict.keys()]:
                    y_i += 3
                y_dict[key] = y_i * d
                y_i += 1
                if draw_bounds:
                    plt.hlines([y_dict[key] + d * 0.05, y_dict[key] + d * 0.95][1:],
                               xmin=-m_max - 0.5, xmax=m_max + 0.5, ls='--', colors='grey')
            x = np.array([s.m - 0.45, s.m + 0.45])  # + x_off[key[:-1]]
            y = np.array([y_dict[key], y_dict[key]])
            ret_x[i] = x
            ret_y[i] = y
            plt.plot(x, y, 'k-')

        x_ticks = np.linspace(-m_max, m_max, int(2 * m_max + 1), dtype=float)
        plt.xticks(x_ticks)
        y_ticks = np.array([[_y[1], (_y[0][0], _y[0][-1])] for _y in y_dict.items()], dtype=object)
        order = np.argsort(y_ticks, axis=0)[:, 0]
        y_ticks = y_ticks[order]
        plt.yticks(y_ticks[:, 0].astype(float), [str(y_l) for y_l in y_ticks[:, 1]])
        plt.xlabel(r'$m$')
        plt.ylabel(r'$(\mathrm{label}, F)$')
        if show:
            plt.tight_layout()
            plt.show()
        return ret_x, ret_y, d


def _cast_delta(delta: array_like, m: Optional[int], size: int) -> ndarray:
    """
    :param delta: An array of frequency shifts for the laser(s). 'delta' must be a scalar or an 1d- or 2d-array
     with shapes (., ) or (., #lasers), respectively.
    :param m: The index of the shifted laser. If delta is a 2d-array, 'm' ist omitted.
    :param size: The number of available lasers.
    :returns: An array of vectors with size 'size' containing frequency shifts for the lasers.
    """
    if delta is None:
        return np.zeros((1, size))
    delta = np.array(delta, dtype=float, order='C')
    if len(delta.shape) != 2 and not -size <= m < size:
        raise IndexError('Laser index \'m\' is out of bounds. Must be {} <= m < {} or None but is {}.'
                         .format(-size, size, m))
    error = False
    if len(delta.shape) > 2:
        error = True
    elif len(delta.shape) == 0:
        if m is None:
            delta = np.full((1, size), delta, dtype=float)
        else:
            delta = np.expand_dims(tools.unit_vector(m, size, dtype=float) * delta, axis=0)
    elif len(delta.shape) == 1:
        if m is None:
            delta = delta[:, None] + np.expand_dims(np.zeros(size), axis=0)
        else:
            delta = tools.unit_vector(np.full(delta.size, m, dtype=int), size, dtype=float) \
                    * np.expand_dims(delta, axis=1)
    elif delta.shape[1] != size:
        error = True
    if error:
        raise ValueError('\'delta\' must be a scalar or an 1d- or 2d-array with shapes '
                         '(., ) or (., #lasers), respectively.')
    return delta


def _choose_solver(solver: str, **kwargs) -> (int, list):
    """
    :param solver: The solver. Can be one of ['rates', 'schroedinger', 'master', 'master_mc'].
    :param kwargs: Keyword arguments to be passed to the chosen solver.
    :returns: The index of the solver and additional arguments that may be required.
    """
    solvers = {'rates': 0, 'schroedinger': 1, 'master': 2, 'master_mc': 3}
    _a = {0: [], 1: [], 2: [], 3: ['dynamics']}
    _d = {'dynamics': False}
    _t = {'dynamics': c_bool}
    try:
        index = solvers[solver.lower()]
    except ValueError:
        raise ValueError('Solver {} is not available. Use one of {}.'
                         .format(solver, ['rates', 'schroedinger', 'master', 'master_mc']))
    _args = [_t[_arg](kwargs.get(_arg, _d[_arg])) for _arg in _a[index]]
    return index, _args


def _cast_y0(y0: Optional[array_like], i_solver: int, atom: Atom):
    """
    :param y0: The initial state of an ensemble of atoms. Depending on the solver, this must be (...).
    :param atom: The atom.
    :param i_solver: The index of the solver.
    :returns: The correctly shaped 'y0' for the chosen solver and its C type.
    """
    size = atom.size
    gs = atom.gs

    if i_solver == 0:  # Rate equations.
        if y0 is None:
            y0 = np.zeros(size, dtype=float)
            y0[gs] = 1 / gs.size
            return y0, c_double_p
        y0 = np.array(y0, dtype=float, order='C')
        if y0.shape[-1] != size:
            raise ValueError('\'y0\' must have size {} in the last axis but has shape {}.'.format(size, y0.shape))
        y0 /= np.expand_dims(np.sum(y0, axis=-1), axis=-1)
        return y0, c_double_p

    elif i_solver == 1:  # Schroedinger equation.
        if y0 is None:
            y0 = np.zeros(size, dtype=complex)
            y0[gs[0]] = 1
            return y0, c_complex_p
        y0 = np.array(y0, dtype=complex, order='C')
        if y0.shape != (size, ):
            raise ValueError('\'y0\' must have shape {} but has shape {}.'.format((size, ), y0.shape))
        y0 /= tools.absolute_complex(y0)
        return y0, c_complex_p

    elif i_solver == 2:  # Master equation.
        if y0 is None:
            y0 = np.zeros(size, dtype=complex)
            y0[gs] = 1 / gs.size
            y0 = np.diag(y0)
            return y0, c_complex_p
        y0 = np.array(y0, dtype=complex, order='C')
        if y0.shape != (size, size) and y0.shape != (size, ):
            raise ValueError('\'y0\' must have shape {} or {} but has shape {}.'
                             .format((size, size), (size, ), y0.shape))
        if len(y0.shape) == 2:
            y0 /= np.sum(np.diag(y0))
        else:
            y0 /= np.sum(y0)
            y0 = np.diag(y0)
        return y0, c_complex_p

    elif i_solver == 3:  # Monte Carlo "master equation".
        if y0 is None:
            y0 = np.zeros((gs.size, size), dtype=complex)
            y0[gs, gs] = 1
            y0 = np.diag(y0)
            return y0, c_complex_p
        y0 = np.array(y0, dtype=complex, order='C')
        if (len(y0.shape) < 2 and y0.shape != (size, )) or len(y0.shape) > 2:
            raise ValueError('\'y0\' must have shape (., {}) or {} but has shape {}.'
                             .format(size, (size, ), y0.shape))
        if len(y0.shape) == 2:
            if y0.shape[1] != size:
                raise ValueError('\'y0\' must have shape (., {}) or {} but has shape {}.'
                                 .format(size, (size, ), y0.shape))
            y0 /= np.expand_dims(tools.absolute_complex(y0, axis=1), axis=1)
        else:
            y0 /= tools.absolute_complex(y0)
            y0 = np.expand_dims(y0, axis=0)

        return y0, c_complex_p


def _cast_v(v: Optional[array_like]):
    """
    :param v: Atom velocities. Must be a scalar or have shape (n, ) or (n, 3). In the first two cases,
     the velocity vector(s) is assumed to be aligned with the x-axis.
    :returns: The correctly shaped velocities with shape (n, 3).
    :raises ValueError: If 'v' has the wrong shape.
    """
    if v is None:
        return np.array([[0, 0, 0]], dtype=float)
    v = np.array(v, dtype=float, order='C')
    if len(v.shape) == 0:
        return np.array([[v, 0, 0]], dtype=float)
    elif len(v.shape) == 1:
        ret = np.zeros((v.size, 3), dtype=float)
        ret[:, 0] = v
        return ret
    elif len(v.shape) == 2:
        if v.shape[1] == 3:
            return v
    raise ValueError('\'v\' must be a scalar or have shape (n, ) or (n, 3) but has shape {}.'.format(v.shape))
    

class Interaction:
    """
    Class representing an Interaction between lasers and an atom.
    """
    def __init__(self, atom: Atom = None, lasers: Iterable[Laser] = None, delta_max: scalar = 1e3,
                 controlled: bool = False, instance=None):
        """
        :param atom: The atom.
        :param lasers: The lasers.
        :param delta_max: The maximum absolute difference between a laser and a transition frequency
         for that transition to be considered laser-driven (MHz). The default value is 1 GHz.
        :param controlled: Whether the ODE solver uses an error controlled stepper or a fixed step size.
         Setting this to True is particularly useful for dynamics where a changing resolution is required.
         However, this comes at the cost of computing time.
        :param instance: A pointer to an existing Interaction instance.
         If this is specified, the other parameters are omitted.
        """
        self.instance = instance
        if self.instance is None:
            self.instance = dll.interaction_construct()
            self._environment = self._get_environemnt()
            if atom is None:
                atom = Atom()
            if lasers is None:
                lasers = []
            self.atom = atom
            self.lasers = list(lasers)
            self.delta_max = delta_max
            self.controlled = controlled
            self.update()
        else:
            self._environment = self._get_environemnt()
            self._atom = self._get_atom()
            self._lasers = self._get_lasers()
            self.update()

    def __del__(self):
        dll.interaction_destruct(self.instance)

    def _get_environemnt(self):
        """
        :return: The environment used in the C++ class.
        """
        return Environment(instance=dll.interaction_get_environment(self.instance))

    def _get_atom(self):
        """
        :return: The atom used in the C++ class.
        """
        return Atom(instance=dll.interaction_get_atom(self.instance))

    def _get_lasers(self):
        """
        :returns: The lasers used in the C++ class.
        """
        return [Laser(0, instance=dll.interaction_get_laser(self.instance, m))
                for m in range(dll.interaction_get_lasers_size(self.instance))]

    def _result(self, instance, **kwargs):
        """
        :param instance: A C++ result instance.
        :returns: The result including the label_map.
        """
        result = Result(instance=instance)
        result.label_map = _gen_label_map(self.atom)
        if kwargs.get('show', True):
            result.plot(**kwargs)
        return result

    def _spectrum(self, instance, **kwargs):
        """
        :param instance: A C++ result instance.
        :returns: The result including the label_map.
        """
        spectrum = Spectrum(instance=instance)
        spectrum.label_map = _gen_label_map(self.atom)
        if kwargs.get('show', True):
            spectrum.plot(**kwargs)
        return spectrum

    def update(self):
        """
        Updates the Interaction.

        :returns: None.
        """
        dll.interaction_update(self.instance)

    def resonance_info(self):
        """
        Prints the detunings of the base frequencies of the lasers in the given atomic system.
        In particular useful for systems with a hyperfine structure. Here

        .. math:: \\Delta = \\nu_0 - \\nu_L.

        :returns: None.
        """
        print('Resonance info:')  # \n<label>(S, L, J, I, F, m) -> <label\'>(S\', L\', J\', I\', F\', m\')')
        for k, (laser, laser_m) in enumerate(zip(self.lasers, self.get_rabi())):
            n = 0
            print('Laser {} @ {} MHz:'.format(k, laser.freq))
            for i, state_i in enumerate(self.atom):
                for j, state_j in enumerate(self.atom):
                    if np.abs(laser_m)[i, j] != 0 and i < j:
                        if state_i.freq < state_j.freq:
                            print('{} -> {}: {} MHz'.format(repr(state_i), repr(state_j),
                                                            state_j.freq - state_i.freq - laser.freq))
                        else:
                            print('{} -> {}: {} MHz'.format(repr(state_j), repr(state_i),
                                                            state_i.freq - state_j.freq - laser.freq))
                        n += 1
            if n == 0:
                print('No resonances!')
        print()

    @property
    def environment(self):
        """
        :returns: The environment of the interaction.
        """
        return self._environment

    @environment.setter
    def environment(self, value: Environment):
        """
        :param value: The new environment of the interaction.
        :returns: None.
        """
        self._environment = value
        dll.interaction_set_environment(self.instance, value.instance)

    @property
    def atom(self):
        """
        :returns: The atom of the interaction.
        """
        return self._atom

    @atom.setter
    def atom(self, value: Atom):
        """
        :param value: The new atom of the interaction.
        :returns: None.
        """
        self._atom = value
        dll.interaction_set_atom(self.instance, value.instance)

    @property
    def lasers(self):
        """
        :returns: The lasers of the interaction.
        """
        return self._lasers

    @lasers.setter
    def lasers(self, value: Iterable[Laser]):
        """
        :param value: The new lasers of the interaction.
        :returns: None.
        """
        self._lasers = list(value)
        dll.interaction_clear_lasers(self.instance)
        for laser in self.lasers:
            dll.interaction_add_laser(self.instance, laser.instance)

    @property
    def delta_max(self):
        """
        :returns: The maximum absolute difference between a laser and a transition frequency
         for that transition to be considered laser-driven (MHz). The default value is 1 GHz.
        """
        return dll.interaction_get_delta_max(self.instance)

    @delta_max.setter
    def delta_max(self, value: scalar):
        """
        :param value: The new maximum absolute difference between a laser and a transition frequency
         for that transition to be considered laser-driven (MHz). The default value is 1 GHz.
        :returns: None.
        """
        dll.interaction_set_delta_max(self.instance, c_double(value))

    @property
    def controlled(self):
        """
        :returns: Whether the ODE solver uses an error controlled stepper or a fixed step size.
         Setting this to True is particularly useful for dynamics where a changing resolution is required.
         However, this comes at the cost of computing time.
        """
        return dll.interaction_get_controlled(self.instance)

    @controlled.setter
    def controlled(self, value: bool):
        """
        :param value: Whether the ODE solver uses an error controlled stepper or a fixed step size.
         Setting this to True is particularly useful for dynamics where a changing resolution is required.
         However, this comes at the cost of computing time.
        :returns: None.
        """
        dll.interaction_set_controlled(self.instance, c_bool(value))

    @property
    def dt(self):
        """
        :returns: The maximum step size of the solver and the rough time spacing of generated results.
         However, this comes at the cost of computing time.
        """
        return dll.interaction_get_dt(self.instance)

    @dt.setter
    def dt(self, value: scalar):
        """
        :param value: The maximum step size of the solver and the rough time spacing of generated results.
        :returns: None.
        """
        dll.interaction_set_dt(self.instance, c_double(value))

    @property
    def loop(self):
        """
        :returns: Whether there are loops formed by the lasers in the atom.
        """
        return dll.interaction_get_loop(self.instance)

    @property
    def time_dependent(self):
        """
        :returns: Whether the system hamiltonian is allowed to be time dependent.
        """
        return dll.interaction_get_time_dependent(self.instance)

    @time_dependent.setter
    def time_dependent(self, value: bool):
        """
        :param value: Set whether the system hamiltonian is allowed to be time dependent.
        :returns: None.
        """
        dll.interaction_set_time_dependent(self.instance, c_bool(value))

    def get_rabi(self, m: int = None):
        """
        :param m: The laser number 'm'. If None, the Rabi frequencies are returned for all lasers
         as an array with shape (#lasers, atom.size, atom.size).
        :returns: The Rabi frequencies (generated by the laser 'm').
        """
        matrix_cd_p = np.ctypeslib.ndpointer(dtype=np.complex128, shape=(self.atom.size, self.atom.size))
        set_restype(dll.interaction_get_rabi, matrix_cd_p)
        if m is None:
            return np.array([dll.interaction_get_rabi(self.instance, c_size_t(_m))
                             for _m in range(len(self.lasers))], dtype=complex)
        return dll.interaction_get_rabi(self.instance, c_size_t(m))

    @property
    def summap(self):
        """
        :returns: A (atom.size x atom.size)-matrix indicating the states which are laser-connected.
        """
        matrix_i_p = np.ctypeslib.ndpointer(dtype=int, shape=(self.atom.size, self.atom.size))
        set_restype(dll.interaction_get_summap, matrix_i_p)
        return dll.interaction_get_summap(self.instance)

    @property
    def atommap(self):
        """
        :returns: A projection matrix A mapping the state frequencies onto the diagonal of the Hamiltonian.
         It holds diag(H)_i <- sum_j(A_ij * state_j.freq).
        """
        matrix_d_p = np.ctypeslib.ndpointer(dtype=float, shape=(self.atom.size, self.atom.size))
        set_restype(dll.interaction_get_atommap, matrix_d_p)
        return dll.interaction_get_atommap(self.instance).T

    @property
    def deltamap(self):
        """
        :returns: A projection matrix B mapping the laser frequencies onto the diagonal of the Hamiltonian.
         It holds diag(H)_i <- sum_j(B_im * laser_m.freq).
        """
        matrix_d_p = np.ctypeslib.ndpointer(dtype=float, shape=(len(self.lasers), self.atom.size))
        set_restype(dll.interaction_get_deltamap, matrix_d_p)
        return dll.interaction_get_deltamap(self.instance).T

    def get_delta(self):
        vector_d_p = np.ctypeslib.ndpointer(dtype=float, shape=(self.atom.size, ))
        set_restype(dll.interaction_get_delta, vector_d_p)
        return dll.interaction_get_delta(self.instance)

    @property
    def history_size(self):
        """
        :returns: The length of the history of states visited during the generation of the diagonal maps.
        """
        return dll.interaction_get_n_history(self.instance)

    @property
    def history(self):
        """
        :returns: The history of states visited during the generation of the diagonal maps.
        """
        vector_i_p = np.ctypeslib.ndpointer(dtype=c_size_t, shape=(self.history_size, ))
        set_restype(dll.interaction_get_history, vector_i_p)
        return dll.interaction_get_history(self.instance)

    def rates(self, t: scalar, y0: array_like = None, **kwargs):
        """
        :param t: The final time of the solution. The number of time steps is determined
         by the step size Interaction.dt.
        :param y0: The initial state of an ensemble of atoms. This must be None or an 1d-array of size
         Interaction.atom.size. If None, the ground states are populated equally.
        :param kwargs: Keyword arguments to be passed to the chosen solver or plot function.
        :returns: The integrated rate equations as a 'Result' object.
        """
        _y0, ctype = _cast_y0(y0, 0, self.atom)
        return self._result(dll.interaction_rate_equations_y0(
            self.instance, c_double(float(t)), _y0.ctypes.data_as(ctype)), **kwargs)

    def rates_new(self, t: scalar, delta: array_like = None, m: Optional[int] = 0, v: array_like = None,
                  y0: array_like = None):
        """
        :param t: The final time of the solution. The number of time steps is determined
         by the step size Interaction.dt.
        :param delta: An array of frequency shifts for the laser(s). 'delta' must be a scalar or a 1d- or 2d-array
         with shapes (., ) or (., #lasers), respectively.
        :param m: The index of the shifted laser. If delta is a 2d-array, 'm' ist omitted.
        :param v: Atom velocities. Must be a scalar or have shape (n, ) or (n, 3). In the first two cases,
         the velocity vector(s) is assumed to be aligned with the x-axis.
        :param y0: The initial state of an ensemble of atoms. This must be None or a 1d-array of size
         Interaction.atom.size. If None, the ground states are populated equally.
        :param kwargs: Keyword arguments to be passed to the chosen solver or plot function.
        :returns: The integrated rate equations as a 'Result' object.
        """
        if isinstance(delta, np.ndarray) and isinstance(v, np.ndarray) and isinstance(y0, np.ndarray):
            if delta.shape == v.shape == y0.shape:
                if delta.flags.f_contiguous:
                    delta = np.ascontiguousarray(delta)
                if v.flags.f_contiguous:
                    v = np.ascontiguousarray(v)
                if y0.flags.f_contiguous:
                    y0 = np.ascontiguousarray(y0)
            vec_size = delta.shape[0]
        else:
            delta = _cast_delta(delta, m, len(self.lasers))
            v = _cast_v(v)
            y0, ctype = _cast_y0(y0, 0, self.atom)

            vec_size = max([delta.shape[0], v.shape[0], 1])

            delta = np.array(np.broadcast_to(delta, (vec_size, len(self.lasers))), dtype=float, order='C')
            v = np.array(np.broadcast_to(v, (vec_size, 3)), dtype=float, order='C')
            y0 = np.array(np.broadcast_to(y0, (vec_size, self.atom.size)), dtype=float, order='C')

        dll.interaction_rate_equations_new(self.instance, c_double(float(t)), delta.ctypes.data_as(c_double_p),
                                           v.ctypes.data_as(c_double_p), y0.ctypes.data_as(c_double_p),
                                           c_size_t(vec_size))
        return y0

    def schroedinger(self, t: scalar, y0: array_like = None, **kwargs):
        """
        :param t: The final time of the solution. The number of time steps is determined
         by the step size Interaction.dt.
        :param y0: The initial state of an ensemble of atoms. This must be None or an 1d-array of size
         Interaction.atom.size. 'y0' can be complex valued. If None, only the first ground state is populated.
         'y0' should be a coherent state vector. However, this is up to the user.
        :param kwargs: Keyword arguments to be passed to the chosen solver or plot function.
        :returns: The integrated Schroedinger equation as a 'Result' object.
        """
        _y0, ctype = _cast_y0(y0, 1, self.atom)
        return self._result(dll.interaction_schroedinger_y0(
            self.instance, c_double(float(t)), _y0.ctypes.data_as(ctype)), **kwargs)

    def master(self, t: scalar, y0: array_like = None, **kwargs):
        """
        :param t: The final time of the solution. The number of time steps is determined
         by the step size Interaction.dt.
        :param y0: The initial state of an ensemble of atoms. This must be None, an 1d-array of size
         Interaction.atom.size or a 2d-array with shape (Interaction.atom.size, Interaction.atom.size).
         'y0' can be complex valued. If None, the ground states are populated equally.
        :param kwargs: Keyword arguments to be passed to the chosen solver or plot function.
        :returns: The integrated master equation as a 'Result' object.
        """
        _y0, ctype = _cast_y0(y0, 2, self.atom)
        return self._result(dll.interaction_master_y0(
            self.instance, c_double(float(t)), _y0.ctypes.data_as(ctype)), **kwargs)

    def master_mc(self, t: scalar, y0: array_like = None, ntraj: int = 500, v: array_like = None,
                  dynamics: bool = False, **kwargs):
        """
        :param t: The final time of the solution. The number of time steps is determined
         by the step size Interaction.dt.
        :param y0: The initial state of an ensemble of atoms. This must be None, an 1d-array of size
         Interaction.atom.size or a 2d-array (i.e. a list of coherent state vectors)
         with shape (n, Interaction.atom.size). 'y0' can be complex valued.
         If None, the ground states are populated equally.
        :param ntraj: The number of trajectories to average over.
        :param v: Atom velocities. This overwrites 'ntraj'.
         Each individual velocity directly corresponds to one trajectory.
        :param dynamics: Whether to simulate the mechanical dynamics of the atom in the laser field.
        :param kwargs: Keyword arguments to be passed to the chosen solver or plot function.
        :returns: The integrated Monte-Carlo master equation as a 'Result' object.
        """
        if self.controlled:
            raise ValueError('Controlled steppers are not supported with \'master_mc\' yet.'
                  ' Decrease the step size if necessary.')
        if dynamics and self.atom.mass <= 0:
            raise ValueError('To simulate mechanical dynamics, the mass of the atom must be specified.')
        _y0, ctype = _cast_y0(y0, 3, self.atom)
        if v is None:
            instance = dll.interaction_master_mc_y0(self.instance, c_double(float(t)), c_size_t(ntraj),
                                                    _y0.ctypes.data_as(ctype), c_size_t(_y0.shape[0]), c_bool(dynamics))
        else:
            v = _cast_v(v)
            instance = dll.interaction_master_mc_v_y0(
                self.instance, v.ctypes.data_as(c_double_p), c_size_t(v.shape[0]), c_double(float(t)),
                _y0.ctypes.data_as(ctype), c_size_t(_y0.shape[0]), c_bool(dynamics))
        return self._result(instance, **kwargs)

    def mean_v(self, t: scalar, v: array_like, y0: array_like = None, solver: str = 'rates', **kwargs):
        """
        :param t: The final time of the solution. The number of time steps is determined
         by the step size Interaction.dt.
        :param v: Atom velocities. Must be a scalar or have shape (n, ) or (n, 3). In the first two cases,
         the velocity vector(s) are assumed to be aligned with the x-axis.
        :param y0: The initial state of an ensemble of atoms. This must be None, an 1d-array of size
         Interaction.atom.size or a 2d-array (i.e. a list of coherent state vectors)
         with shape (n, Interaction.atom.size). 'y0' can be complex valued.
         If None, the ground states are populated according to the chosen solver.
        :param solver: The solver. Can be one of ['rates', 'schroedinger', 'master', 'master_mc'].
        :param kwargs: Keyword arguments to be passed to the chosen solver or plot function.
        :returns: The mean of the solutions for the specified velocities and solver as a 'Result' object.
        """
        _solver, _args = _choose_solver(solver, **kwargs)
        if _solver == 3:
            return self.master_mc(t, y0, v=v, dynamics=kwargs.get('dynamics', False))
        v = _cast_v(v)
        _y0, ctype = _cast_y0(y0, _solver, self.atom)
        dll_funcs = [dll.interaction_mean_v_y0_vectord, dll.interaction_mean_v_y0_vectorcd,
                     dll.interaction_mean_v_y0_matrixcd]
        return self._result(dll_funcs[_solver](self.instance, v.ctypes.data_as(c_double_p), c_size_t(v.shape[0]),
                                               c_double(t), _y0.ctypes.data_as(ctype)), **kwargs)

    def spectrum(self, t: scalar, delta: array_like, m: Optional[int] = 0, v: array_like = None, y0: array_like = None,
                 solver: str = 'rates', v_mode: str = 'mean', **kwargs):
        """
        :param t: The final time of the solution. The number of time steps is determined
         by the step size Interaction.dt.
        :param delta: An array of frequency shifts for the laser(s). 'delta' must be a scalar or a 1d- or 2d-array
         with shapes (., ) or (., #lasers), respectively.
        :param m: The index of the shifted laser. If delta is a 2d-array, 'm' ist omitted.
        :param v: Atom velocities. Must be a scalar or have shape (n, ) or (n, 3). In the first two cases,
         the velocity vector(s) is assumed to be aligned with the x-axis.
        :param y0: The initial state of an ensemble of atoms. This must be None, a 1d-array of size
         Interaction.atom.size or a 2d-array (i.e. a list of coherent state vectors)
         with shape (n, Interaction.atom.size). 'y0' can be complex valued.
         If None, the ground states are populated according to the chosen solver.
        :param solver: The solver. Can be one of ['rates', 'schroedinger', 'master', 'master_mc'].
        :param v_mode: The mode how to combine the different velocities. Available modes are ['mean', ].
        :param kwargs: Keyword arguments to be passed to the chosen solver.
        :returns: The results for the different frequency shifts as a 'Spectrum' object.
        """
        delta = _cast_delta(delta, m, len(self.lasers))
        _solver, _args = _choose_solver(solver, **kwargs)
        v = tools.asarray_optional(v, dtype=float)
        _y0, ctype = _cast_y0(y0, _solver, self.atom)
        if v is None:
            dll_funcs = [dll.interaction_spectrum_y0_vectord, dll.interaction_spectrum_y0_vectorcd,
                         dll.interaction_spectrum_y0_matrixcd]
            if _solver == 3:
                v = np.zeros((kwargs.get('ntraj', 500), 3), dtype=float)
                instance = dll.interaction_spectrum_mean_v_y0_vector_vectorcd(
                    self.instance, delta.ctypes.data_as(c_double_p), c_size_t(delta.shape[0]),
                    v.ctypes.data_as(c_double_p), c_size_t(v.shape[0]), c_double(t), _y0.ctypes.data_as(ctype),
                    _y0.shape[0], *_args)
            else:
                instance = dll_funcs[_solver](self.instance, delta.ctypes.data_as(c_double_p), c_size_t(delta.shape[0]),
                                              c_double(t), _y0.ctypes.data_as(ctype))
        else:
            v = _cast_v(v)
            dll_funcs = [dll.interaction_spectrum_mean_v_y0_vectord, dll.interaction_spectrum_mean_v_y0_vectorcd,
                         dll.interaction_spectrum_mean_v_y0_matrixcd]
            if _solver == 3:
                instance = dll.interaction_spectrum_mean_v_y0_vector_vectorcd(
                    self.instance, delta.ctypes.data_as(c_double_p), c_size_t(delta.shape[0]),
                    v.ctypes.data_as(c_double_p), c_size_t(v.shape[0]), c_double(t), _y0.ctypes.data_as(ctype),
                    _y0.shape[0], *_args)
            else:
                instance = dll_funcs[_solver](
                    self.instance, delta.ctypes.data_as(c_double_p), c_size_t(delta.shape[0]),
                    v.ctypes.data_as(c_double_p), c_size_t(v.shape[0]), c_double(t), _y0.ctypes.data_as(ctype))

        return self._spectrum(instance=instance, t=(0, t), **{**{'m': m}, **kwargs})


class Result:
    """
    Class serving as a container for results from Interaction instances.
    """

    def __init__(self, instance=None):
        """
        :param instance: A pointer to an existing Result instance.
        """
        self.instance = instance
        self.label_map = _gen_label_map(self._y_size())

    def __del__(self):
        dll.result_destruct(self.instance)

    def _x_size(self):
        """
        :returns: The number of entries in the definition space.
        """
        return dll.result_get_x_size(self.instance)

    def _y_size(self):
        """
        :returns: The dimension of the image space.
        """
        return dll.result_get_y_size(self.instance)

    def _v_size(self):
        """
        :returns: The dimension of the image space.
        """
        return dll.result_get_v_size(self.instance)

    @property
    def x(self):
        """
        :returns: The entries of the definition space (x-axis) as an array. This has shape (n, ).
        """
        vector_result_d_p = np.ctypeslib.ndpointer(dtype=np.float64, shape=(self._x_size(),))
        set_restype(dll.result_get_x, vector_result_d_p)
        return dll.result_get_x(self.instance)

    @property
    def y(self):
        """
        :returns: The entries of the image space (y-axes) as an array. This has shape (n, m).
        """
        matrix_result_d_p = np.ctypeslib.ndpointer(dtype=np.float64, shape=(self._x_size(), self._y_size()))
        set_restype(dll.result_get_y, matrix_result_d_p)
        return dll.result_get_y(self.instance)

    @property
    def v(self):
        """
        :returns: The entries of the image space (y-axes) as an array. This has shape (n, 3).
        """
        if self._v_size() == 0:
            return None
        matrix_result_d_p = np.ctypeslib.ndpointer(dtype=np.float64, shape=(self._v_size(), 3))
        set_restype(dll.result_get_v, matrix_result_d_p)
        return dll.result_get_v(self.instance)

    def plot(self, labels: Iterable[str] = None, show: bool = True, colormap: str = None, x_scale: str = 'linear'):
        """
        :param labels: An Iterable of state labels to include in the plot if a system is known.
         Default is None which plots all states.
        :param show: Whether to show the plot.
        :param colormap: A matplotlib colormap to use for the plot colors.
        :param x_scale: The scale of the time axis. Takes the same arguments as matplotlibs 'ax.set_xscale'.
        :returns: The newly created figure.
        """
        fig, ax = plt.subplots()
        x, y = self.x, self.y
        colors = _define_colors(y.shape[1], self.label_map, colormap=colormap)

        for label, indices in self.label_map.items():
            if labels is not None and label not in labels:
                continue
            for i, index in enumerate(indices):
                ax.plot(x, y[:, index], c=colors[index], ls='--')
            ax.plot(x, np.sum(y[:, indices], axis=1), label=label,
                    c=colors[indices[0]], ls='-')

        ax.set_xscale(x_scale)
        ax.set_ylim(-0.03, 1.03)
        ax.set_xlabel(r'Time ($\mu$s)')
        ax.set_ylabel(r'State population')
        plt.legend()
        if show:
            plt.show()
        return fig

    def hist(self, v_rec=None):
        v = self.v.copy()
        if v is None:
            return
        if v_rec is not None:
            v /= v_rec
            plt.xlabel('number of recoils')
        else:
            plt.xlabel('velocity change (m/s)')
        plt.ylabel('abundance')
        bins = min([int(v.shape[0] / 100), 100])
        plt.hist(v[:, 0], bins=bins, density=True, alpha=0.7, label='x')
        plt.hist(v[:, 1], bins=bins, density=True, alpha=0.7, label='y')
        plt.hist(v[:, 2], bins=bins, density=True, alpha=0.7, label='z')
        plt.legend(loc=1)
        plt.show()


class Spectrum:
    """
    Class serving as a container for spectra.
    """

    def __init__(self, instance=None):
        """
        :param instance: A pointer to an existing Spectrum instance.
        """
        self.instance = instance
        self.label_map = _gen_label_map(self._y_size())

    def __del__(self):
        dll.spectrum_destruct(self.instance)

    def _m_size(self):
        """
        :returns: The number of lasers.
        """
        return dll.spectrum_get_m_size(self.instance)

    def _x_size(self):
        """
        :returns: The number of detunings.
        """
        return dll.spectrum_get_x_size(self.instance)

    def _t_size(self):
        """
        :returns: The number of times.
        """
        return dll.spectrum_get_t_size(self.instance)

    def _y_size(self):
        """
        :returns: The number of atomic states.
        """
        return dll.spectrum_get_y_size(self.instance)

    @property
    def x(self):
        """
        :returns: The entries of the first definition space (delta-axis) as an array.
         This has shape (n_delta, n_lasers).
        """
        matrix_d_p = np.ctypeslib.ndpointer(dtype=np.float64, shape=(self._x_size(), self._m_size()))
        set_restype(dll.spectrum_get_x, matrix_d_p)
        return dll.spectrum_get_x(self.instance)

    @property
    def t(self):
        """
        :returns: The entries of the second definition space (t-axis) as an array. This has shape (n_t, ).
        """
        vector_d_p = np.ctypeslib.ndpointer(dtype=np.float64, shape=(self._t_size(),))
        set_restype(dll.spectrum_get_t, vector_d_p)
        return dll.spectrum_get_t(self.instance)

    @property
    def y(self):
        """
        :returns: The entries of the image space (y-axes) as an array. This has shape (n_delta, n_t, n_states).
        """
        tensor_d_p = np.ctypeslib.ndpointer(dtype=np.float64, shape=(self._x_size(), self._t_size(), self._y_size()))
        set_restype(dll.spectrum_get_y, tensor_d_p)
        return dll.spectrum_get_y(self.instance)

    def plot(self, t: Union[tuple, list], m: Optional[int] = 0, labels: Iterable[str] = None,
             show: bool = True, colormap: str = None):
        """

        :param t: A time interval which is summed over to display the spectrum.
        :param m: The index of the shown laser. If delta is a 1d-array, 'm' ist omitted.
        :param labels: An Iterable of state labels to include in the plot if a system is known.
         Default is None which plots all states.
        :param show: Whether to show the plot.
        :param colormap: A matplotlib colormap to use for the plot colors.
        :returns: The newly created figure.
        """
        fig, ax = plt.subplots()
        if m is None:
            m = 0
        m = int(m)
        x, _t = self.x[:, m], self.t
        in_t = np.nonzero(~((_t < t[0]) + (_t > t[1])))[0]
        y = np.sum(self.y[:, in_t, :], axis=1) * (_t[1] - _t[0])
        colors = _define_colors(y.shape[1], self.label_map, colormap=colormap)

        for label, indices in self.label_map.items():
            if labels is not None and label not in labels:
                continue
            for i, index in enumerate(indices):
                ax.plot(x, y[:, index], c=colors[index], ls='--')
            ax.plot(x, np.sum(y[:, indices], axis=1), label=label,
                    c=colors[indices[0]], ls='-')

        # ax.set_ylim(-0.03, 1.03)
        ax.set_xlabel(r'Detuning (MHz)')
        ax.set_ylabel(r'State population')
        plt.legend()
        if show:
            plt.show()
        return fig


def _define_colors(n: int, label_map: dict, colormap: str = None):
    """
    :param n: The size of the system.
    :param label_map: A dictionary with state labels as keys
     and an array of the indices of the states with the labels as values.
    :param colormap: A matplotlib colormap.
    :returns: A list of colors with size n.
    """
    cmap = cm.get_cmap(colormap)
    labels = [(k, v) for k, v in label_map.items()]
    labels = sorted(labels, key=lambda kv: min(kv[1]))
    colors = ['', ] * n
    for i, (label, indices) in enumerate(labels):
        for index in indices:
            if colormap is None:
                colors[index] = tools.COLORS.PYPLOT[i % 10]
            else:
                colors[index] = cmap(i / (len(labels) - 1))
    return colors
