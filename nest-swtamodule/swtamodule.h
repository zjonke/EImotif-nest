/*
 *  swtamodule.h
 */

#ifndef SWTAMODULE_H
#define SWTAMODULE_H

// Includes from sli:
#include "slifunction.h"
#include "slimodule.h"

// Put your stuff into your own namespace.
namespace swtamodule_ns
{

/**
 * Class defining your model.
 * @note For each model, you must define one such class, with a unique name.
 */
class SWTAModule : public SLIModule
{
public:
  // Interface functions ------------------------------------------

  /**
   * @note The constructor registers the module with the dynamic loader.
   *       Initialization proper is performed by the init() method.
   */
  SWTAModule();

  /**
   * @note The destructor does not do much in modules.
   */
  ~SWTAModule();

  /**
   * Initialize module.
   * @param SLIInterpreter* SLI interpreter
   */
  void init( SLIInterpreter* );

  /**
   * Return the name of your model.
   */
  const std::string name( void ) const;

  /**
   * Return the name of a sli file to execute when swtamodule is loaded.
   * This mechanism can be used to define SLI commands associated with your
   * module, in particular, set up type tries for functions you have defined.
   */
  const std::string commandstring( void ) const;
};
} // namespace swtamodule_ns

#endif
