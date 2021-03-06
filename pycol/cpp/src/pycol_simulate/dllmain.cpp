// dllmain.cpp : Defines the entry point for the DLL application.
#include "pch.h"
#include "Utility.h"
#include "Light.h"
#include "Matter.h"
#include "Interaction.h"
#include <complex>

BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
                     )
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}

extern "C"
{   

    // Polarization
    __declspec(dllexport) Polarization* polarization_construct()
    {
        return new Polarization();
    }

    __declspec(dllexport) void polarization_destruct(Polarization* polarization)
    {
        delete polarization;
    }

    __declspec(dllexport) void polarization_init(Polarization* polarization, std::complex<double>* vec,
        double* q_axis, bool vec_as_q)
    {
        Vector3cd _vec;
        _vec << vec[0], vec[1], vec[2];
        Vector3d _q_axis;
        _q_axis << q_axis[0], q_axis[1], q_axis[2];
        polarization->init(_vec, _q_axis, vec_as_q);
    }

    __declspec(dllexport) void polarization_def_q_axis(Polarization* polarization, double* q_axis, bool q_fixed)
    {
        Vector3d _q_axis;
        _q_axis << q_axis[0], q_axis[1], q_axis[2];
        polarization->def_q_axis(_q_axis, q_fixed);
    }

    __declspec(dllexport) double* polarization_get_q_axis(Polarization* polarization)
    {
        return polarization->get_q_axis()->data();
    }

    __declspec(dllexport) std::complex<double>* polarization_get_x(Polarization* polarization)
    {
        return polarization->get_x()->data();
    }

    __declspec(dllexport) std::complex<double>* polarization_get_q(Polarization* polarization)
    {
        return polarization->get_q()->data();
    }


    // Laser
    __declspec(dllexport) Laser* laser_construct()
    {
        return new Laser();
    }

    __declspec(dllexport) void laser_destruct(Laser* laser)
    {
        delete laser;
    }

    __declspec(dllexport) void laser_init(Laser* laser, double freq, double intensity, Polarization* polarization)
    {
        laser->init(freq, intensity, polarization);
    }

    __declspec(dllexport) double laser_get_freq(Laser* laser)
    {
        return laser->get_freq();
    }

    __declspec(dllexport) void laser_set_freq(Laser* laser, double freq)
    {
        return laser->set_freq(freq);
    }

    __declspec(dllexport) double laser_get_intensity(Laser* laser)
    {
        return laser->get_intensity();
    }

    __declspec(dllexport) void laser_set_intensity(Laser* laser, double intensity)
    {
        return laser->set_intensity(intensity);
    }

    __declspec(dllexport) Polarization* laser_get_polarization(Laser* laser)
    {
        return laser->get_polarization();
    }

    __declspec(dllexport) void laser_set_polarization(Laser* laser, Polarization* polarization)
    {
        return laser->set_polarization(polarization);
    }

    __declspec(dllexport) double* laser_get_k(Laser* laser)
    {
        return laser->get_k()->data();
    }

    __declspec(dllexport) void laser_set_k(Laser* laser, double* k)
    {
        Vector3d _k;
        _k << k[0], k[1], k[2];
        _k /= _k.norm();
        return laser->set_k(_k);
    }


    //Environment
    __declspec(dllexport) Environment* environment_construct()
    {
        return new Environment();
    }

    __declspec(dllexport) void environment_destruct(Environment* env)
    {
        delete env;
    }

    __declspec(dllexport) double environment_get_E(Environment* env)
    {
        return env->get_E();
    }

    __declspec(dllexport) double environment_get_B(Environment* env)
    {
        return env->get_B();
    }

    __declspec(dllexport) double* environment_get_e_E(Environment* env)
    {
        return env->get_e_E()->data();
    }

    __declspec(dllexport) double* environment_get_e_B(Environment* env)
    {
        return env->get_e_B()->data();
    }

    __declspec(dllexport) void environment_set_E(Environment* env, double* E)
    {
        Vector3d _E;
        _E << E[0], E[1], E[2];
        env->set_E(_E);
    }

    __declspec(dllexport) void environment_set_B(Environment* env, double* B)
    {
        Vector3d _B;
        _B << B[0], B[1], B[2];
        env->set_B(_B);
    }

    __declspec(dllexport) void environment_set_E_double(Environment* env, double E)
    {
        env->set_E(E);
    }

    __declspec(dllexport) void environment_set_B_double(Environment* env, double B)
    {
        env->set_B(B);
    }


    // State
    __declspec(dllexport) State* state_construct()
    {
        return new State();
    }

    __declspec(dllexport) void state_destruct(State* state)
    {
        delete state;
    }

    __declspec(dllexport) void state_init(State* state, double _freq_0, double _s, double _l, double _j, double _i, double _f,
        double _m, double* _hyper_const, double _g, char* _label)
    {
        state->init(_freq_0, _s, _l, _j, _i, _f, _m, _hyper_const, _g, std::string(_label));
    }

    __declspec(dllexport) void state_update(State* state)
    {
        return state->update();
    }

    __declspec(dllexport) void state_update_env(State* state, Environment* env)
    {
        return state->update(env);
    }

    __declspec(dllexport) double state_get_shift(State* state)
    {
        return state->get_shift();
    }

    __declspec(dllexport) double state_get_freq_j(State* state)
    {
        return state->get_freq_j();
    }

    __declspec(dllexport) void state_set_freq_j(State* state, double freq_j)
    {
        state->set_freq_j(freq_j);
    }

    __declspec(dllexport) double state_get_freq(State* state)
    {
        return state->get_freq();
    }

    __declspec(dllexport) double state_get_s(State* state)
    {
        return state->get_s();
    }

    __declspec(dllexport) void state_set_s(State* state, double s)
    {
        state->set_s(s);
    }

    __declspec(dllexport) double state_get_l(State* state)
    {
        return state->get_l();
    }

    __declspec(dllexport) void state_set_l(State* state, double l)
    {
        state->set_l(l);
    }

    __declspec(dllexport) double state_get_j(State* state)
    {
        return state->get_j();
    }

    __declspec(dllexport) void state_set_j(State* state, double j)
    {
        state->set_j(j);
    }

    __declspec(dllexport) double state_get_i(State* state)
    {
        return state->get_i();
    }

    __declspec(dllexport) void state_set_i(State* state, double i)
    {
        state->set_i(i);
    }

    __declspec(dllexport) double state_get_f(State* state)
    {
        return state->get_f();
    }

    __declspec(dllexport) void state_set_f(State* state, double f)
    {
        state->set_f(f);
    }

    __declspec(dllexport) double state_get_m(State* state)
    {
        return state->get_m();
    }

    __declspec(dllexport) void state_set_m(State* state, double m)
    {
        state->set_m(m);
    }

    __declspec(dllexport) double* state_get_hyper_const(State* state)
    {
        return state->get_hyper_const();
    }

    __declspec(dllexport) void state_set_hyper_const(State* state, double* hyper_const)
    {
        state->set_hyper_const(hyper_const);
    }

    __declspec(dllexport) double state_get_g(State* state)
    {
        return state->get_g();
    }

    __declspec(dllexport) void state_set_g(State* state, double g)
    {
        state->set_g(g);
    }

    __declspec(dllexport) const char* state_get_label(State* state)
    {
        char* ret = new char[state->get_label().length() + 1];
        strcpy_s(ret, state->get_label().length() + 1, state->get_label().c_str());
        return ret;
    }

    __declspec(dllexport) void state_set_label(State* state, char* label)
    {
        state->set_label(std::string(label));
    }


    // DecayMap
    __declspec(dllexport) DecayMap* decaymap_construct()
    {
        return new DecayMap();
    }

    __declspec(dllexport) void decaymap_destruct(DecayMap* decay_map)
    {
        delete decay_map;
    }

    __declspec(dllexport) void decaymap_add_decay(DecayMap* decays, char* state_0, char* state_1, double a)
    {
        decays->add_decay(std::string(state_0), std::string(state_1), a);
    }

    __declspec(dllexport) const char* decaymap_get_label(DecayMap* decays, size_t i, size_t j)
    {
        if (i == 0)
        {
            char* ret = new char[decays->get_states_0()->at(j).length() + 1];
            strcpy_s(ret, decays->get_states_0()->at(j).length() + 1, decays->get_states_0()->at(j).c_str());
            return ret;
        }
        else if (i == 1)
        {
            char* ret = new char[decays->get_states_1()->at(j).length() + 1];
            strcpy_s(ret, decays->get_states_1()->at(j).length() + 1, decays->get_states_1()->at(j).c_str());
            return ret;
        }
        else return "";

    }

    __declspec(dllexport) double* decaymap_get_a(DecayMap* decays)
    {
        return decays->get_a()->data();
    }


    __declspec(dllexport) size_t decaymap_get_size(DecayMap* decays)
    {
        return decays->get_size();
    }

    // Atom
    __declspec(dllexport) Atom* atom_construct()
    {
        return new Atom();
    }

    __declspec(dllexport) void atom_destruct(Atom* atom)
    {
        delete atom;
    }

    __declspec(dllexport) void atom_update(Atom* atom)
    {
        atom->update();
    }

    __declspec(dllexport) void atom_add_state(Atom* atom, State* state)
    {
        atom->add_state(state);
    }

    __declspec(dllexport) void atom_clear_states(Atom* atom)
    {
        atom->clear_states();
    }

    __declspec(dllexport) DecayMap* atom_get_decay_map(Atom* atom)
    {
        return atom->get_decay_map();
    }

    __declspec(dllexport) void atom_set_decay_map(Atom* atom, DecayMap* decay_map)
    {
        return atom->set_decay_map(decay_map);
    }

    __declspec(dllexport) double atom_get_mass(Atom* atom)
    {
        return atom->get_mass();
    }

    __declspec(dllexport) void atom_set_mass(Atom* atom, double mass)
    {
        atom->set_mass(mass);
    }

    __declspec(dllexport) size_t atom_get_size(Atom* atom)
    {
        return atom->get_size();
    }

    __declspec(dllexport) size_t atom_get_gs_size(Atom* atom)
    {
        return atom->get_gs()->size();
    }

    __declspec(dllexport) size_t* atom_get_gs(Atom* atom)
    {
        return atom->get_gs()->data();
    }

    __declspec(dllexport) double* atom_get_m_dipole(Atom* atom, size_t i)
    {
        return atom->get_m_dipole()->at(i).data();
    }

    __declspec(dllexport) double* atom_get_L0(Atom* atom)
    {
        return atom->get_L0()->data();
    }

    __declspec(dllexport) double* atom_get_L1(Atom* atom)
    {
        return atom->get_L1()->data();
    }


    // Interaction
    __declspec(dllexport) Interaction* interaction_construct()
    {
        return new Interaction();
    }

    __declspec(dllexport) void interaction_destruct(Interaction* interaction)
    {
        delete interaction;
    }

    __declspec(dllexport) void interaction_update(Interaction* interaction)
    {
        interaction->update();
    }

    __declspec(dllexport) Environment* interaction_get_environment(Interaction* interaction)
    {
        return interaction->get_env();
    }

    __declspec(dllexport) void interaction_set_environment(Interaction* interaction, Environment* environment)
    {
        interaction->set_env(environment);
    }

    __declspec(dllexport) Atom* interaction_get_atom(Interaction* interaction)
    {
        return interaction->get_atom();
    }

    __declspec(dllexport) void interaction_set_atom(Interaction* interaction, Atom* atom)
    {
        interaction->set_atom(atom);
    }

    __declspec(dllexport) void interaction_add_laser(Interaction* interaction, Laser* laser)
    {
        interaction->add_laser(laser);
    }

    __declspec(dllexport) void interaction_clear_lasers(Interaction* interaction)
    {
        interaction->clear_lasers();

    }

    __declspec(dllexport) size_t interaction_get_lasers_size(Interaction* interaction)
    {
        return interaction->get_lasers()->size();
    }

    __declspec(dllexport) Laser* interaction_get_laser(Interaction* interaction, size_t m)
    {
        return interaction->get_lasers()->at(m);
    }

    __declspec(dllexport) double interaction_get_delta_max(Interaction* interaction)
    {
        return interaction->get_delta_max();
    }

    __declspec(dllexport) void interaction_set_delta_max(Interaction* interaction, double delta_max)
    {
        interaction->set_delta_max(delta_max);
    }

    __declspec(dllexport) bool interaction_get_controlled(Interaction* interaction)
    {
        return interaction->get_controlled();
    }

    __declspec(dllexport) void interaction_set_controlled(Interaction* interaction, bool controlled)
    {
        interaction->set_controlled(controlled);
    }

    __declspec(dllexport) double interaction_get_dt(Interaction* interaction)
    {
        return interaction->get_dt();
    }

    __declspec(dllexport) void interaction_set_dt(Interaction* interaction, double dt)
    {
        interaction->set_dt(dt);
    }

    __declspec(dllexport) int* interaction_get_summap(Interaction* interaction)
    {
        return interaction->get_summap()->data();
    }

    __declspec(dllexport) std::complex<double>* interaction_get_rabi(Interaction* interaction, size_t m)
    {
        MatrixXcd* rabi = new MatrixXcd(interaction->get_atom()->get_size(), interaction->get_atom()->get_size());
        *rabi = interaction->get_rabimap()->at(m) * 2;
        return rabi->data();
    }

    __declspec(dllexport) double* interaction_get_atommap(Interaction* interaction)
    {
        return interaction->get_atommap()->data();
    }

    __declspec(dllexport) double* interaction_get_deltamap(Interaction* interaction)
    {
        return interaction->get_deltamap()->data();
    }

    __declspec(dllexport) double* interaction_get_delta(Interaction* interaction)
    {
        VectorXd* delta = new VectorXd(interaction->get_atom()->get_size());
        *delta = interaction->gen_delta(*interaction->gen_w0(), *interaction->gen_w());
        return delta->data();
    }

    __declspec(dllexport) bool interaction_get_loop(Interaction* interaction)
    {
        return interaction->get_loop();
    }

    __declspec(dllexport) bool interaction_get_time_dependent(Interaction* interaction)
    {
        return interaction->get_time_dependent();
    }

    __declspec(dllexport) void interaction_set_time_dependent(Interaction* interaction, bool time_dependent)
    {
        interaction->set_time_dependent(time_dependent);
    }

    __declspec(dllexport) size_t* interaction_get_history(Interaction* interaction)
    {
        return interaction->history.data();
    }

    __declspec(dllexport) int interaction_get_n_history(Interaction* interaction)
    {
        return interaction->n_history;
    }

    __declspec(dllexport) Result* interaction_rate_equations(Interaction* interaction, double t)
    {
        return interaction->rate_equations(t);
    }

    __declspec(dllexport) Result* interaction_rate_equations_y0(Interaction* interaction, double t, double* y0)
    {
        size_t n = interaction->arange_t(t);
        size_t size = interaction->get_atom()->get_size();
        VectorXd _y0(size);
        _y0 = VectorXd::Zero(size);
        for (size_t i = 0; i < size; ++i) _y0(i) = y0[i];
        return interaction->rate_equations(n, _y0);
    }

    __declspec(dllexport) void interaction_rate_equations_new(Interaction* interaction, double t, double* delta, double* v, double* y0, size_t vec_size)
    {
        size_t n = interaction->arange_t(t);
        size_t size = interaction->get_atom()->get_size();
        const std::vector<VectorXd> _delta = cast_delta(delta, vec_size, interaction->get_lasers()->size());
        const std::vector<Vector3d> _v = cast_v(v, vec_size);
        std::vector<VectorXd> _y0 = cast_delta(y0, vec_size, size);
        interaction->rate_equations(n, _delta, _v, _y0);
        for (size_t i = 0; i < vec_size; ++i)
        {
            for (size_t j = 0; j < size; ++j)
            {
                y0[i * size + j] = _y0.at(i)(j);
            }
        }
    }

    __declspec(dllexport) Result* interaction_schroedinger(Interaction* interaction, double t)
    {
        return interaction->schroedinger(t);
    }

    __declspec(dllexport) Result* interaction_schroedinger_y0(Interaction* interaction, double t, std::complex<double>* y0)
    {
        size_t n = interaction->arange_t(t);
        size_t size = interaction->get_atom()->get_size();
        VectorXcd _y0(size);
        _y0 = VectorXcd::Zero(size);
        for (size_t i = 0; i < size; ++i) _y0(i) = y0[i];
        return interaction->schroedinger(n, _y0);
    }

    __declspec(dllexport) Result* interaction_master(Interaction* interaction, double t)
    {
        return interaction->master(t);
    }

    __declspec(dllexport) Result* interaction_master_y0(Interaction* interaction, double t, std::complex<double>* y0, bool dynamics)
    {
        size_t n = interaction->arange_t(t);
        size_t size = interaction->get_atom()->get_size();
        MatrixXcd _y0(size, size);
        _y0 = MatrixXcd::Zero(size, size);
        for (size_t j = 0; j < size; ++j)
        {
            for (size_t i = 0; i < size; ++i) _y0(i, j) = y0[size * j + i];
        }
        return interaction->master(n, _y0);
    }

    __declspec(dllexport) Result* interaction_master_mc(Interaction* interaction, double t, size_t num, bool dynamics)
    {
        return interaction->master_mc(t, num, dynamics);
    }

    __declspec(dllexport) Result* interaction_master_mc_v(Interaction* interaction, double* v, size_t v_size, double t, bool dynamics)
    {
        size_t n = interaction->arange_t(t);
        VectorXd delta = VectorXd::Zero(interaction->get_lasers()->size());
        std::vector<Vector3d> _v = cast_v(v, v_size);
        return interaction->master_mc(n, delta, _v, dynamics);
    }

    __declspec(dllexport) Result* interaction_master_mc_y0(Interaction* interaction, double t, size_t num,
        std::complex<double>* y0, size_t y0_size, bool dynamics)
    {
        size_t n = interaction->arange_t(t);
        size_t size = interaction->get_atom()->get_size();
        std::vector<VectorXcd> _y0 = cast_y0_vector_vectorcd(y0, y0_size, size);
        return interaction->master_mc(n, _y0, num, dynamics);
    }

    __declspec(dllexport) Result* interaction_master_mc_v_y0(Interaction* interaction, double* v, size_t v_size, double t,
        std::complex<double>* y0, size_t y0_size, bool dynamics)
    {
        size_t n = interaction->arange_t(t);
        size_t size = interaction->get_atom()->get_size();
        std::vector<VectorXcd> _y0 = cast_y0_vector_vectorcd(y0, y0_size, size);
        VectorXd delta = VectorXd::Zero(interaction->get_lasers()->size());
        std::vector<Vector3d> _v = cast_v(v, v_size);
        return interaction->master_mc(n, _y0, delta, _v, dynamics);
    }

    __declspec(dllexport) Result* interaction_mean_v(Interaction* interaction, double* v, size_t v_size,
        double t, int solver)
    {
        return interaction->mean_v(cast_v(v, v_size), t, solver);
    }

    __declspec(dllexport) Result* interaction_mean_v_y0_vectord(Interaction* interaction, double* v, size_t v_size,
        double t, double* y0)
    {
        size_t n = interaction->arange_t(t);
        VectorXd _y0 = cast_y0_vectord(y0, interaction->get_atom()->get_size());
        return interaction->mean_v(cast_v(v, v_size), n, _y0, 0);
    }

    __declspec(dllexport) Result* interaction_mean_v_y0_vectorcd(Interaction* interaction, double* v, size_t v_size,
        double t, std::complex<double>* y0)
    {
        size_t n = interaction->arange_t(t);
        VectorXcd _y0 = cast_y0_vectorcd(y0, interaction->get_atom()->get_size());
        return interaction->mean_v(cast_v(v, v_size), n, _y0, 1);
    }

    __declspec(dllexport) Result* interaction_mean_v_y0_matrixcd(Interaction* interaction, double* v, size_t v_size,
        double t, std::complex<double>* y0)
    {
        size_t n = interaction->arange_t(t);
        MatrixXcd _y0 = cast_y0_matrixcd(y0, interaction->get_atom()->get_size());
        return interaction->mean_v(cast_v(v, v_size), n, _y0, 2);
    }

    __declspec(dllexport) Spectrum* interaction_spectrum(Interaction* interaction, double* delta, size_t delta_size,
        double t, int solver)
    {
        // Map<MatrixXd> _delta(delta, interaction->get_lasers()->size(), delta_size);
        return interaction->spectrum(cast_delta(delta, delta_size, interaction->get_lasers()->size()), t, solver);
    }

    __declspec(dllexport) Spectrum* interaction_spectrum_y0_vectord(Interaction* interaction, double* delta, size_t delta_size,
        double t, double* y0)
    {
        size_t n = interaction->arange_t(t);
        VectorXd _y0 = cast_y0_vectord(y0, interaction->get_atom()->get_size());
        const std::vector<VectorXd> _delta = cast_delta(delta, delta_size, interaction->get_lasers()->size());
        return interaction->spectrum(_delta, n, _y0, 0);
    }

    __declspec(dllexport) Spectrum* interaction_spectrum_y0_vectorcd(Interaction* interaction, double* delta, size_t delta_size,
        double t, std::complex<double>* y0)
    {
        size_t n = interaction->arange_t(t);
        VectorXcd _y0 = cast_y0_vectorcd(y0, interaction->get_atom()->get_size());
        const std::vector<VectorXd> _delta = cast_delta(delta, delta_size, interaction->get_lasers()->size());
        return interaction->spectrum(_delta, n, _y0, 1);
    }

    __declspec(dllexport) Spectrum* interaction_spectrum_y0_matrixcd(Interaction* interaction, double* delta, size_t delta_size,
        double t, std::complex<double>* y0)
    {
        size_t n = interaction->arange_t(t);
        MatrixXcd _y0 = cast_y0_matrixcd(y0, interaction->get_atom()->get_size());
        const std::vector<VectorXd> _delta = cast_delta(delta, delta_size, interaction->get_lasers()->size());
        return interaction->spectrum(_delta, n, _y0, 2);
    }

    __declspec(dllexport) Spectrum* interaction_spectrum_mean_v(Interaction* interaction, double* delta, size_t delta_size,
        double* v, size_t v_size, double t, int solver)
    {
        return interaction->spectrum(cast_delta(delta, delta_size, interaction->get_lasers()->size()), cast_v(v, v_size), t, solver);
    }

    __declspec(dllexport) Spectrum* interaction_spectrum_mean_v_y0_vectord(Interaction* interaction, double* delta, size_t delta_size,
        double* v, size_t v_size, double t, double* y0)
    {
        size_t n = interaction->arange_t(t);
        VectorXd _y0 = cast_y0_vectord(y0, interaction->get_atom()->get_size());
        const std::vector<VectorXd> _delta = cast_delta(delta, delta_size, interaction->get_lasers()->size());
        return interaction->spectrum(_delta, cast_v(v, v_size), n, _y0, 0);
    }

    __declspec(dllexport) Spectrum* interaction_spectrum_mean_v_y0_vectorcd(Interaction* interaction, double* delta, size_t delta_size,
        double* v, size_t v_size, double t, std::complex<double>* y0)
    {
        size_t n = interaction->arange_t(t);
        VectorXcd _y0 = cast_y0_vectorcd(y0, interaction->get_atom()->get_size());
        const std::vector<VectorXd> _delta = cast_delta(delta, delta_size, interaction->get_lasers()->size());
        return interaction->spectrum(_delta, cast_v(v, v_size), n, _y0, 1);
    }

    __declspec(dllexport) Spectrum* interaction_spectrum_mean_v_y0_matrixcd(Interaction* interaction, double* delta, size_t delta_size,
        double* v, size_t v_size, double t, std::complex<double>* y0)
    {
        size_t n = interaction->arange_t(t);
        MatrixXcd _y0 = cast_y0_matrixcd(y0, interaction->get_atom()->get_size());
        const std::vector<VectorXd> _delta = cast_delta(delta, delta_size, interaction->get_lasers()->size());
        return interaction->spectrum(_delta, cast_v(v, v_size), n, _y0, 2);
    }

    __declspec(dllexport) Spectrum* interaction_spectrum_mean_v_y0_vector_vectorcd(Interaction* interaction, double* delta, size_t delta_size,
        double* v, size_t v_size, double t, std::complex<double>* y0, size_t y0_size, bool dynamics)
    {
        size_t n = interaction->arange_t(t);
        std::vector<VectorXcd> _y0 = cast_y0_vector_vectorcd(y0, y0_size, interaction->get_atom()->get_size());
        const std::vector<VectorXd> _delta = cast_delta(delta, delta_size, interaction->get_lasers()->size());
        return interaction->spectrum_mc(_delta, cast_v(v, v_size), n, _y0, 2, dynamics);
    }


    // Result
    __declspec(dllexport) Result* result_construct()
    {
        return new Result();
    }

    __declspec(dllexport) void result_destruct(Result* result)
    {
        result->~Result();
    }

    __declspec(dllexport) double* result_get_x(Result* result)
    {
        return result->get_x()->data();
    }

    __declspec(dllexport) double* result_get_y(Result* result)
    {
        return result->get_y_numpy()->data();
    }

    __declspec(dllexport) double* result_get_v(Result* result)
    {
        return result->get_v_numpy()->data();
    }

    __declspec(dllexport) size_t result_get_x_size(Result* result)
    {

        return result->get_x_size();
    }

    __declspec(dllexport) size_t result_get_y_size(Result* result)
    {
        return result->get_y_size();
    }

    __declspec(dllexport) size_t result_get_v_size(Result* result)
    {
        return result->get_v_size();
    }


    // Spectrum
    __declspec(dllexport) Spectrum* spectrum_construct()
    {
        return new Spectrum();
    }

    __declspec(dllexport) void spectrum_destruct(Spectrum* spectrum)
    {
        spectrum->~Spectrum();
    }

    __declspec(dllexport) double* spectrum_get_x(Spectrum* spectrum)
    {
        return spectrum->get_x()->data();
    }

    __declspec(dllexport) double* spectrum_get_t(Spectrum* spectrum)
    {
        return spectrum->get_t()->data();
    }

    __declspec(dllexport) double* spectrum_get_y(Spectrum* spectrum)
    {
        return spectrum->get_y()->data();
    }

    __declspec(dllexport) size_t spectrum_get_m_size(Spectrum* spectrum)
    {
        return spectrum->get_m_size();
    }

    __declspec(dllexport) size_t spectrum_get_x_size(Spectrum* spectrum)
    {
        return spectrum->get_x_size();
    }

    __declspec(dllexport) size_t spectrum_get_t_size(Spectrum* spectrum)
    {
        return spectrum->get_t_size();
    }

    __declspec(dllexport) size_t spectrum_get_y_size(Spectrum* spectrum)
    {
        return spectrum->get_y_size();
    }


    // @ScatteringRate
    __declspec(dllexport) void sr_generate_y(std::complex<double>* denominator, std::complex<double>* f_theta,
        std::complex<double>* f_phi, int* counts, int* shape, double* y)
    {
        int s0 = shape[0];
        int s1 = shape[1];
        int len_counts = shape[2];
        int len_y = s0 * s1;
        int sum_counts = 0;
        for (int i = 0; i < len_counts; ++i) {
            sum_counts += counts[i];
        }
        int i = 0;
        int ij = 0;
        for (int x = 0; x < s0; ++x) {
            for (int a = 0; a < s1; ++a) {
                i = 0;
                for (int c = 0; c < len_counts; ++c) {
                    std::complex<double> c_theta(0., 0.);
                    std::complex<double> c_phi(0., 0.);
                    for (int j = 0; j < counts[c]; ++j) {
                        ij = i + j;
                        c_theta += denominator[x * sum_counts + ij] * f_theta[a * sum_counts + ij];
                        c_phi += denominator[x * sum_counts + ij] * f_phi[a * sum_counts + ij];
                    }
                    i = ij + 1;
                    //y[x * s1 + a] += (c_theta * std::conj(c_theta) + c_phi * std::conj(c_phi)).real();
                    y[x * s1 + a] += std::norm(c_theta) + std::norm(c_phi);
                }
            }
        }
    }

};
