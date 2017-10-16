/*
 *  stdp_connection_sem.h
 */

#ifndef STDP_CONNECTION_SEM_H
#define STDP_CONNECTION_SEM_H

/* BeginDocumentation
  Name: sem_synapse - Synapse type for spike-timing dependent
   plasticity with additional additive factors.

  Description:
   sem_synapse is a connector to create synapses with spike time
   dependent plasticity. Unlike stdp_synapse, we use the update equations:

   \Delta w = \lambda * w_{max} * (K_+(w) * F_+(t) - A)            if t - t_j^(k) > 0
   \Delta w = \lambda * w_{max} * (-alpha * K_-(w) * F_-(t) - A)   else

   where

   K_+(w) = exp(\nu_+ w)
   K_-(w) = exp(\nu_- w)

   and

   F_+(t) = exp((t - t_j^(k))/tau_+)
   F_-(t) = exp((t - t_j^(k))/tau_-)

   This makes it possible to implement update rules which approximate the
   rule of [1], e.g. the rules given in [2] and [3].

  Parameters:
   lambda          double - Step size
   Wmax            double - Maximum allowed weight, note that this scales each
                            weight update
   scale_with_Wmax  bool  - if True, the weight w is replaced in the update
                            equations by w/Wmax as is the default behavior of
                            standard Nest synapses. If False, the factor
                            w_{max} in the calculation of \Delta w is dropped.
                            (default: True)
   alpha           double - Determine shape of depression term
   nu_plus         double - Set weight dependency of facilitating update
   nu_minus        double - Set weight dependency of depressing update
   tau_plus        double - Time constant of STDP window, potentiation in ms
   A               double - Set negative offset for both updates

   (tau_minus is defined in the post-synaptic neuron.)

  Transmits: SpikeEvent

  References:
   [1] Nessler, Bernhard, et al. "Bayesian computation emerges in generic
       cortical microcircuits through spike-timing-dependent plasticity." PLoS
       computational biology 9.4 (2013): e1003037.
   [2] Legenstein, Robert, et al. "Assembly pointers for variable binding in
       networks of spiking neurons." arXiv preprint arXiv:1611.03698 (2016).
   [3] Jonke, Zeno, et al. "Feedback inhibition shapes emergent computational
       properties of cortical microcircuit motifs." arXiv preprint
       arXiv:1705.07614 (2017).

  Adapted from stdp_synapse:
      FirstVersion: March 2006
      Author: Moritz Helias, Abigail Morrison
      Adapted by: Philipp Weidel

  Author: Michael Mueller

  SeeAlso: synapsedict, stdp_synapse
*/

// C++ includes:
#include <cmath>

// Includes from nestkernel:
#include "common_synapse_properties.h"
#include "connection.h"
#include "connector_model.h"
#include "event.h"

// Includes from sli:
#include "dictdatum.h"
#include "dictutils.h"


namespace swtamodule_ns
{

using namespace nest;

// connections are templates of target identifier type (used for pointer /
// target index addressing) derived from generic connection template
template < typename targetidentifierT >
class STDPConnectionSem : public Connection< targetidentifierT >
{

public:
  typedef CommonSynapseProperties CommonPropertiesType;
  typedef Connection< targetidentifierT > ConnectionBase;

  /**
   * Default Constructor.
   * Sets default values for all parameters. Needed by GenericConnectorModel.
   */
  STDPConnectionSem();


  /**
   * Copy constructor.
   * Needs to be defined properly in order for GenericConnector to work.
   */
  STDPConnectionSem( const STDPConnectionSem& );

  // Explicitly declare all methods inherited from the dependent base
  // ConnectionBase. This avoids explicit name prefixes in all places these
  // functions are used. Since ConnectionBase depends on the template parameter,
  // they are not automatically found in the base class.
  using ConnectionBase::get_delay_steps;
  using ConnectionBase::get_delay;
  using ConnectionBase::get_rport;
  using ConnectionBase::get_target;

  /**
   * Get all properties of this connection and put them into a dictionary.
   */
  void get_status( DictionaryDatum& d ) const;

  /**
   * Set properties of this connection from the values given in dictionary.
   */
  void set_status( const DictionaryDatum& d, ConnectorModel& cm );

  /**
   * Send an event to the receiver of this connection.
   * \param e The event to send
   * \param t_lastspike Point in time of last spike sent.
   * \param cp common properties of all synapses (empty).
   */
  void send( Event& e,
    thread t,
    double t_lastspike,
    const CommonSynapseProperties& cp );


  class ConnTestDummyNode : public ConnTestDummyNodeBase
  {
  public:
    // Ensure proper overriding of overloaded virtual functions.
    // Return values from functions are ignored.
    using ConnTestDummyNodeBase::handles_test_event;
    port
    handles_test_event( SpikeEvent&, rport )
    {
      return invalid_port_;
    }
  };

  void
  check_connection( Node& s,
    Node& t,
    rport receptor_type,
    double t_lastspike,
    const CommonPropertiesType& )
  {
    ConnTestDummyNode dummy_target;

    ConnectionBase::check_connection_( dummy_target, s, t, receptor_type );

    t.register_stdp_connection( t_lastspike - get_delay() );
  }

  void
  set_weight( double w )
  {
    weight_ = w;
  }

private:
  double
  facilitate_(double w, double kplus)
  {
    if(learning_is_active_ == 0.0)
      return w;

    if (scale_with_Wmax_)
    {
      w = w / Wmax_;
    }

    double K_w = std::exp(nu_plus_ * w);
    double F_t = kplus;

    double dW = lambda_ * (K_w * F_t - A_);
    double new_w = w + dW;

    if (scale_with_Wmax_)
    {
      // new_w is normalized
      return new_w < 1.0 ? new_w * Wmax_ : Wmax_;
    } else {
      // new_w is the absolute proposed value
      return new_w < Wmax_ ? new_w : Wmax_;
    }
  }

  double
  depress_(double w, double kminus)
  {
    if(learning_is_active_ == 0.0)
      return w;

    if (scale_with_Wmax_)
    {
      w = w / Wmax_;
    }

    double K_w = std::exp(nu_minus_ * w);
    double F_t = kminus;

    double dW = lambda_ * (-alpha_ * K_w * F_t - A_);
    double new_w = w + dW;

    if (scale_with_Wmax_)
    {
      // new_w is normalized
      return new_w > 0.0 ? new_w * Wmax_ : 0.0;
    } else {
      // new_w is the absolute proposed value
      return new_w > 0.0 ? new_w : 0.0;
    }
  }

  // data members of each connection
  double weight_;
  double Wmax_;
  double lambda_;
  double alpha_;
  double nu_plus_;
  double nu_minus_;
  double A_;
  double tau_plus_;
  bool scale_with_Wmax_;
  double Kplus_;
  double learning_is_active_;
};


/**
 * Send an event to the receiver of this connection.
 * \param e The event to send
 * \param t The thread on which this connection is stored.
 * \param t_lastspike Time point of last spike emitted
 * \param cp Common properties object, containing the stdp parameters.
 */
template < typename targetidentifierT >
inline void
STDPConnectionSem< targetidentifierT >::send( Event& e,
  thread t,
  double t_lastspike,
  const CommonSynapseProperties& )
{
  // synapse STDP depressing/facilitation dynamics
  //   if(t_lastspike >0) {std::cout << "last spike " << t_lastspike <<
  //   std::endl ;}
  double t_spike = e.get_stamp().get_ms();
  // t_lastspike_ = 0 initially

  // use accessor functions (inherited from Connection< >) to obtain delay and
  // target
  Node* target = get_target( t );
  double dendritic_delay = get_delay();

  // get spike history in relevant range (t1, t2] from post-synaptic neuron
  std::deque< histentry >::iterator start;
  std::deque< histentry >::iterator finish;

  // For a new synapse, t_lastspike contains the point in time of the last
  // spike. So we initially read the
  // history(t_last_spike - dendritic_delay, ..., T_spike-dendritic_delay]
  // which increases the access counter for these entries.
  // At registration, all entries' access counters of
  // history[0, ..., t_last_spike - dendritic_delay] have been
  // incremented by Archiving_Node::register_stdp_connection(). See bug #218 for
  // details.
  target->get_history(
    t_lastspike - dendritic_delay, t_spike - dendritic_delay, &start, &finish );
  // facilitation due to post-synaptic spikes since last pre-synaptic spike
  double minus_dt;
  while (start != finish)
  {
    minus_dt = t_lastspike - ( start->t_ + dendritic_delay );
    ++start;

    if ( minus_dt == 0 )
      continue;

    weight_ = facilitate_(weight_, Kplus_ * std::exp(minus_dt / tau_plus_));
  }

  // depression due to new pre-synaptic spike
  weight_ = depress_(weight_, target->get_K_value(t_spike - dendritic_delay));

  e.set_receiver( *target );
  e.set_weight( weight_ );
  // use accessor functions (inherited from Connection< >) to obtain delay in
  // steps and rport
  e.set_delay( get_delay_steps() );
  e.set_rport( get_rport() );
  e();

  Kplus_ = Kplus_ * std::exp( ( t_lastspike - t_spike ) / tau_plus_ ) + 1.0;
}

template < typename targetidentifierT >
STDPConnectionSem< targetidentifierT >::STDPConnectionSem()
  : ConnectionBase()
  , weight_( 1.0 )
  , Wmax_( 100.0 )
  , lambda_( 0.01 )
  , alpha_( 1.0 )
  , nu_plus_( 0.0 )
  , nu_minus_( 0.0 )
  , A_( 0.0 )
  , tau_plus_( 20.0 )
  , scale_with_Wmax_( 0.0 )
  , Kplus_( 0.0 )
  , learning_is_active_(1.0)
{
}

template < typename targetidentifierT >
STDPConnectionSem< targetidentifierT >::STDPConnectionSem(
  const STDPConnectionSem< targetidentifierT >& rhs )
  : ConnectionBase( rhs )
  , weight_( rhs.weight_ )
  , Wmax_( rhs.Wmax_ )
  , lambda_( rhs.lambda_ )
  , alpha_( rhs.alpha_ )
  , nu_plus_( rhs.nu_plus_ )
  , nu_minus_( rhs.nu_minus_ )
  , A_( rhs.A_ )
  , tau_plus_( rhs.tau_plus_ )
  , scale_with_Wmax_( rhs.scale_with_Wmax_ )
  , learning_is_active_( rhs.learning_is_active_ )
  , Kplus_( rhs.Kplus_ )
{
}

template < typename targetidentifierT >
void
STDPConnectionSem< targetidentifierT >::get_status( DictionaryDatum& d ) const
{
  ConnectionBase::get_status( d );
  def< double >( d, names::weight, weight_ );
  def< double >( d, "Wmax", Wmax_ );
  def< double >( d, "lambda", lambda_ );
  def< double >( d, "alpha", alpha_ );
  def< double >( d, "nu_plus", nu_plus_ );
  def< double >( d, "nu_minus", nu_minus_ );
  def< double >( d, "A", A_ );
  def< double >( d, "tau_plus", tau_plus_ );
  def< bool >( d, "scale_with_Wmax", scale_with_Wmax_ );
  def< double >( d, "learning_is_active", learning_is_active_ );
  def< long >( d, names::size_of, sizeof( *this ) );
}

template < typename targetidentifierT >
void
STDPConnectionSem< targetidentifierT >::set_status( const DictionaryDatum& d,
  ConnectorModel& cm )
{
  ConnectionBase::set_status( d, cm );
  updateValue< double >( d, names::weight, weight_ );
  updateValue< double >( d, "Wmax", Wmax_ );
  updateValue< double >( d, "lambda", lambda_ );
  updateValue< double >( d, "alpha", alpha_ );
  updateValue< double >( d, "nu_plus", nu_plus_ );
  updateValue< double >( d, "nu_minus", nu_minus_ );
  updateValue< double >( d, "A", A_ );
  updateValue< double >( d, "tau_plus", tau_plus_ );
  updateValue< bool >( d, "scale_with_Wmax", scale_with_Wmax_ );
  updateValue< double >( d, "learning_is_active", learning_is_active_ );

  // check if weight_ and Wmax_ has the same sign
  if ( not( ( ( weight_ >= 0 ) - ( weight_ < 0 ) )
         == ( ( Wmax_ >= 0 ) - ( Wmax_ < 0 ) ) ) )
  {
    throw BadProperty( "Weight and Wmax must have same sign." );
  }
}

} // of namespace nest

#endif // of #ifndef STDP_CONNECTION_H
