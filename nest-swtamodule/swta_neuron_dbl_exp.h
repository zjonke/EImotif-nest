/*
 *  swta_neuron_dbl_exp.h
 */

#ifndef SWTA_NEURON_DBL_EXP_H
#define SWTA_NEURON_DBL_EXP_H

// Includes from librandom:
#include "gamma_randomdev.h"
#include "poisson_randomdev.h"

// Includes from nestkernel:
#include "archiving_node.h"
#include "connection.h"
#include "event.h"
#include "nest_types.h"
#include "ring_buffer.h"
#include "universal_data_logger.h"

namespace nest
{

/* BeginDocumentation
   Name: swta_neuron_dbl_exp - modified swta_neuron using double exponential
      PSPs.

  Description:

  Modifications are:
       1. Using a rise and a fill time for PSC integration.
       2. Removed parameter C_m.
       3. Currents are not integrated, but multiplied with a new parameter
          I_scale and simply added to the membrane potential.

  This model implements a stochastically firing neuron with rate

      rho = c_1 * V' + c_2 * (exp(c_3 * V') - c_4)

  which is rectified (rates < 0 are not possible).

  The effective membrane potential is

      V' = V + E_sfa

  where V is the actual membrane potential, and E_sfa arises from an
  (optional) spike-frequency adaptation (SFA) mechanism. Every time the neuron
  spikes, E_sfa is increase by the quantity q_sfa. It can also be clipped
  to some upper (or lower value), see the description of the parameters below.

  After each spike, V is reset to V_reset if with_reset is True.

  The PSPs have an exponential shape: each incoming spike produces a jump of
  V with height w * z_scale, after which the PSP decays with tau_m.

  For more information, see the description of the parameters or compare the
  documentation of the original model pp_psc_delta.

  Parameters:

  The following parameters can be set in the status dictionary.

  V_m               double - Membrane potential in mV at simulation begin.
  tau_r             double - PSP rise time in ms.
  tau_f             double - PSP fall time in ms.
  q_sfa             double - Adaptive threshold jump in mV.
  tau_sfa           double - Adaptive threshold time constant in ms.
  dead_time         double - Duration of the dead time in ms.
  dead_time_random  bool   - Should a random dead time be drawn after each
                             spike?
  dead_time_shape   int    - Shape parameter of dead time gamma distribution.
  t_ref_remaining   double - Remaining dead time at simulation start.
  with_reset        bool   - Should the membrane potential be reset after a
                             spike?
  I_e               double - Constant input current in pA.
  c_1               double - Slope of linear part of transfer function in
                             Hz/mV.
  c_2               double - Prefactor of exponential part of transfer function
                             in Hz.
  c_3               double - Coefficient of exponential non-linearity of
                             transfer function in 1/mV.
  c_4               double - Offset coefficient for exponential.
  V_reset           double - Membrane reset potential in mV.
  z_scale           double - Scaling of incoming spike responses.
  I_scale           double - Scaling of incoming currents.
  E_sfa_clip        bool   - Use the max value for E_sfa?
  E_sfa_max         double - Maximum or minimum allow value for E_sfa,
                             depending on sign of q_sfa.


  Sends: SpikeEvent

  Receives: SpikeEvent, CurrentEvent, DataLoggingRequest

  Adapted from pp_psc_delta: Author:  July 2009, Deger, Helias; January
  2011, Zaytsev; May 2014, Setareh

  Version: August 2017
  Author: Michael Mueller

  SeeAlso: pp_pop_psc_delta, iaf_psc_delta, iaf_psc_alpha, iaf_psc_exp,
  iaf_psc_delta_canon
*/

/**
 * Point process neuron with leaky integration of delta-shaped PSCs.
 */
class swta_neuron_dbl_exp : public Archiving_Node
{

public:
  swta_neuron_dbl_exp();
  swta_neuron_dbl_exp( const swta_neuron_dbl_exp& );

  /**
   * Import sets of overloaded virtual functions.
   * @see Technical Issues / Virtual Functions: Overriding, Overloading, and
   * Hiding
   */
  using Node::handle;
  using Node::handles_test_event;

  port send_test_event( Node&, rport, synindex, bool );

  void handle( SpikeEvent& );
  void handle( CurrentEvent& );
  void handle( DataLoggingRequest& );

  port handles_test_event( SpikeEvent&, rport );
  port handles_test_event( CurrentEvent&, rport );
  port handles_test_event( DataLoggingRequest&, rport );


  void get_status( DictionaryDatum& ) const;
  void set_status( const DictionaryDatum& );

private:
  void init_state_( const Node& proto );
  void init_buffers_();
  void calibrate();

  void update( Time const&, const long, const long );

  // The next two classes need to be friends to access the State_ class/member
  friend class RecordablesMap< swta_neuron_dbl_exp >;
  friend class UniversalDataLogger< swta_neuron_dbl_exp >;

  // ----------------------------------------------------------------

  /**
   * Independent parameters of the model.
   */
  struct Parameters_
  {

    /** PSP rise time in ms. */
    double tau_r_;

    /** PSP fall time in ms. */
    double tau_f_;

    /** Dead time in ms. */
    double dead_time_;

    /** Do we use random dead time? */
    bool dead_time_random_;

    /** Shape parameter of random dead time gamma distribution. */
    unsigned long dead_time_shape_;

    /** Do we reset the membrane potential after each spike? */
    bool with_reset_;

    /** List of adaptive threshold time constant in ms (for multi adaptation
     * version). */
    std::vector< double > tau_sfa_;

    /** Adaptive threshold jump in mV (for multi adaptation version). */
    std::vector< double > q_sfa_;

    /** indicates multi parameter adaptation model **/
    bool multi_param_;

    /** Slope of the linear part of transfer function. */
    double c_1_;

    /** Prefactor of exponential part of transfer function. */
    double c_2_;

    /** Coefficient of exponential non-linearity of transfer function. */
    double c_3_;

    /** Offset coefficient for exponential. */
    double c_4_;

    /** External DC current. */
    double I_e_;

    /** Membrane reset potential. */
    double V_reset_;

    /** Incoming spike scale factor. */
    double z_scale_;

    /** Incoming current scale factor (conductance). */
    double I_scale_;

    /** Dead time from simulation start. */
    double t_ref_remaining_;

    /** Use the max value for E_sfa? */
    bool E_sfa_clip_;

    /** Maximum or minimum allow value for E_sfa, depending on sign. */
    double E_sfa_max_;

    Parameters_(); //!< Sets default parameter values

    void get( DictionaryDatum& ) const; //!< Store current values in dictionary
    void set( const DictionaryDatum& ); //!< Set values from dictionary
  };

  // ----------------------------------------------------------------

  /**
   * State variables of the model.
   */
  struct State_
  {
    double y0_; //!< This is piecewise constant external current
    //! This is the membrane potential RELATIVE TO RESTING POTENTIAL.
    double y3_;
    double q_; //!< This is the change of the 'threshold' due to adaptation.

    double u_rise_;  //!< Contribution of rise exponential to membrane potential.
    double u_fall_;  //!< Contribution of fall exponential to membrane potential.

    //! Vector of adaptation parameters. by Hesam
    std::vector< double > q_elems_;

    int r_; //!< Number of refractory steps remaining

    bool initialized_; //!< it is true if the vectors are initialized

    State_(); //!< Default initialization

    void get( DictionaryDatum&, const Parameters_& ) const;
    void set( const DictionaryDatum&, const Parameters_& );
  };

  // ----------------------------------------------------------------

  /**
   * Buffers of the model.
   */
  struct Buffers_
  {
    Buffers_( swta_neuron_dbl_exp& );
    Buffers_( const Buffers_&, swta_neuron_dbl_exp& );

    /** buffers and sums up incoming spikes/currents */
    RingBuffer spikes_;
    RingBuffer currents_;

    //! Logger for all analog data
    UniversalDataLogger< swta_neuron_dbl_exp > logger_;
  };

  // ----------------------------------------------------------------

  /**
   * Internal variables of the model.
   */
  struct Variables_
  {

    double u_rise_dt_;
    double u_fall_dt_;

    std::vector< double > Q33_;

    double h_;       //!< simulation time step in ms
    double dt_rate_; //!< rate parameter of dead time distribution

    librandom::RngPtr rng_; //!< random number generator of my own thread
    librandom::PoissonRandomDev poisson_dev_; //!< random deviate generator
    librandom::GammaRandomDev gamma_dev_;     //!< random deviate generator

    int DeadTimeCounts_;
  };

  // Access functions for UniversalDataLogger -----------------------

  //! Read out the real membrane potential
  double
  get_V_m_() const
  {
    return S_.y3_;
  }

  //! Read out the adaptive threshold potential
  double
  get_E_sfa_() const
  {
    return S_.q_;
  }

  // ----------------------------------------------------------------

  /**
   * @defgroup iaf_psc_alpha_data
   * Instances of private data structures for the different types
   * of data pertaining to the model.
   * @note The order of definitions is important for speed.
   * @{
   */
  Parameters_ P_;
  State_ S_;
  Variables_ V_;
  Buffers_ B_;
  /** @} */

  //! Mapping of recordables names to access functions
  static RecordablesMap< swta_neuron_dbl_exp > recordablesMap_;
};

inline port
swta_neuron_dbl_exp::send_test_event( Node& target,
  rport receptor_type,
  synindex,
  bool )
{
  SpikeEvent e;
  e.set_sender( *this );

  return target.handles_test_event( e, receptor_type );
}


inline port
swta_neuron_dbl_exp::handles_test_event( SpikeEvent&, rport receptor_type )
{
  if ( receptor_type != 0 )
  {
    throw UnknownReceptorType( receptor_type, get_name() );
  }
  return 0;
}

inline port
swta_neuron_dbl_exp::handles_test_event( CurrentEvent&, rport receptor_type )
{
  if ( receptor_type != 0 )
  {
    throw UnknownReceptorType( receptor_type, get_name() );
  }
  return 0;
}

inline port
swta_neuron_dbl_exp::handles_test_event( DataLoggingRequest& dlr, rport receptor_type )
{
  if ( receptor_type != 0 )
  {
    throw UnknownReceptorType( receptor_type, get_name() );
  }
  return B_.logger_.connect_logging_device( dlr, recordablesMap_ );
}

inline void
swta_neuron_dbl_exp::get_status( DictionaryDatum& d ) const
{
  P_.get( d );
  S_.get( d, P_ );
  Archiving_Node::get_status( d );
  ( *d )[ names::recordables ] = recordablesMap_.get_list();
}

inline void
swta_neuron_dbl_exp::set_status( const DictionaryDatum& d )
{
  Parameters_ ptmp = P_; // temporary copy in case of errors
  ptmp.set( d );         // throws if BadProperty
  State_ stmp = S_;      // temporary copy in case of errors
  stmp.set( d, ptmp );   // throws if BadProperty

  // We now know that (ptmp, stmp) are consistent. We do not
  // write them back to (P_, S_) before we are also sure that
  // the properties to be set in the parent class are internally
  // consistent.
  Archiving_Node::set_status( d );

  // if we get here, temporaries contain consistent set of properties
  P_ = ptmp;
  S_ = stmp;
}

} // namespace

#endif /* #ifndef SWTA_NEURON_DBL_EXP_H */
