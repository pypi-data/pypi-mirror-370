#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.fluent.core.solver.flobject import *

from ansys.fluent.core.solver.flobject import (
    _ChildNamedObjectAccessorMixin,
    _NonCreatableNamedObjectMixin,
    _InputFile,
    _OutputFile,
    _InOutFile,
)

SHASH = "95073fe7f7871428d6991a093452e57ae0a32c0c2bf95b83255b04796185d6a8"

class file_type(String, AllowedValuesMixin):
    """
    'file_type' child.
    """
    _version = '222'
    fluent_name = 'file-type'
    _python_name = 'file_type'
    return_type = 'object'

class file_name(Filename):
    """
    'file_name' child.
    """
    _version = '222'
    fluent_name = 'file-name'
    _python_name = 'file_name'
    return_type = 'object'

class read(Command):
    """
    'read' command.
    """
    _version = '222'
    fluent_name = 'read'
    _python_name = 'read'
    argument_names = ['file_type', 'file_name']
    _child_classes = dict(
        file_type=file_type,
        file_name=file_name,
    )
    return_type = 'object'

class replace_mesh(Command):
    """
    'replace_mesh' command.
    """
    _version = '222'
    fluent_name = 'replace-mesh'
    _python_name = 'replace_mesh'
    argument_names = ['file_name']
    _child_classes = dict(
        file_name=file_name,
    )
    return_type = 'object'

class write(Command):
    """
    'write' command.
    """
    _version = '222'
    fluent_name = 'write'
    _python_name = 'write'
    argument_names = ['file_type', 'file_name']
    _child_classes = dict(
        file_type=file_type,
        file_name=file_name,
    )
    return_type = 'object'

class project_filename(String):
    """
    'project_filename' child.
    """
    _version = '222'
    fluent_name = 'project-filename'
    _python_name = 'project_filename'
    return_type = 'object'

class new(Command):
    """
    Create New Project.
    
    Parameters
    ----------
        project_filename : str
            'project_filename' child.
    """
    _version = '222'
    fluent_name = 'new'
    _python_name = 'new'
    argument_names = ['project_filename']
    _child_classes = dict(
        project_filename=project_filename,
    )
    return_type = 'object'

class load_case(Boolean):
    """
    'load_case' child.
    """
    _version = '222'
    fluent_name = 'load-case'
    _python_name = 'load_case'
    return_type = 'object'

class open(Command):
    """
    Open project.
    
    Parameters
    ----------
        project_filename : str
            'project_filename' child.
        load_case : bool
            'load_case' child.
    """
    _version = '222'
    fluent_name = 'open'
    _python_name = 'open'
    argument_names = ['project_filename', 'load_case']
    _child_classes = dict(
        project_filename=project_filename,
        load_case=load_case,
    )
    return_type = 'object'

class save(Command):
    """
    Save Project.
    """
    _version = '222'
    fluent_name = 'save'
    _python_name = 'save'
    return_type = 'object'

class save_as(Command):
    """
    Save As Project.
    
    Parameters
    ----------
        project_filename : str
            'project_filename' child.
    """
    _version = '222'
    fluent_name = 'save-as'
    _python_name = 'save_as'
    argument_names = ['project_filename']
    _child_classes = dict(
        project_filename=project_filename,
    )
    return_type = 'object'

class convert_to_managed(Boolean):
    """
    'convert_to_managed' child.
    """
    _version = '222'
    fluent_name = 'convert-to-managed'
    _python_name = 'convert_to_managed'
    return_type = 'object'

class save_as_copy(Command):
    """
    Save As Project.
    
    Parameters
    ----------
        project_filename : str
            'project_filename' child.
        convert_to_managed : bool
            'convert_to_managed' child.
    """
    _version = '222'
    fluent_name = 'save-as-copy'
    _python_name = 'save_as_copy'
    argument_names = ['project_filename', 'convert_to_managed']
    _child_classes = dict(
        project_filename=project_filename,
        convert_to_managed=convert_to_managed,
    )
    return_type = 'object'

class archive_name(String):
    """
    'archive_name' child.
    """
    _version = '222'
    fluent_name = 'archive-name'
    _python_name = 'archive_name'
    return_type = 'object'

class archive(Command):
    """
    Archive Project.
    
    Parameters
    ----------
        archive_name : str
            'archive_name' child.
    """
    _version = '222'
    fluent_name = 'archive'
    _python_name = 'archive'
    argument_names = ['archive_name']
    _child_classes = dict(
        archive_name=archive_name,
    )
    return_type = 'object'

class parametric_project(Group):
    """
    'parametric_project' child.
    """
    _version = '222'
    fluent_name = 'parametric-project'
    _python_name = 'parametric_project'
    command_names = ['new', 'open', 'save', 'save_as', 'save_as_copy', 'archive']
    _child_classes = dict(
        new=new,
        open=open,
        save=save,
        save_as=save_as,
        save_as_copy=save_as_copy,
        archive=archive,
    )
    return_type = 'object'

class file(Group):
    """
    'file' child.
    """
    _version = '222'
    fluent_name = 'file'
    _python_name = 'file'
    command_names = ['read', 'replace_mesh', 'write', 'parametric_project']
    _child_classes = dict(
        read=read,
        replace_mesh=replace_mesh,
        write=write,
        parametric_project=parametric_project,
    )
    return_type = 'object'

class type(String, AllowedValuesMixin):
    """
    Solver type.
    """
    _version = '222'
    fluent_name = 'type'
    _python_name = 'type'
    return_type = 'object'

class two_dim_space(String, AllowedValuesMixin):
    """
    'two_dim_space' child.
    """
    _version = '222'
    fluent_name = 'two-dim-space'
    _python_name = 'two_dim_space'
    return_type = 'object'

class velocity_formulation(String, AllowedValuesMixin):
    """
    Velocity formulation.
    """
    _version = '222'
    fluent_name = 'velocity-formulation'
    _python_name = 'velocity_formulation'
    return_type = 'object'

class time(String, AllowedValuesMixin):
    """
    'time' child.
    """
    _version = '222'
    fluent_name = 'time'
    _python_name = 'time'
    return_type = 'object'

class solver(Group):
    """
    'solver' child.
    """
    _version = '222'
    fluent_name = 'solver'
    _python_name = 'solver'
    child_names = ['type', 'two_dim_space', 'velocity_formulation', 'time']
    _child_classes = dict(
        type=type,
        two_dim_space=two_dim_space,
        velocity_formulation=velocity_formulation,
        time=time,
    )
    return_type = 'object'

class adjust_solver_defaults_based_on_setup(Boolean):
    """
    Enable/disable adjustment of solver defaults based on setup.
    """
    _version = '222'
    fluent_name = 'adjust-solver-defaults-based-on-setup'
    _python_name = 'adjust_solver_defaults_based_on_setup'
    return_type = 'object'

class gravity_1(Boolean):
    """
    Gravitational acceleration.
    """
    _version = '222'
    fluent_name = 'gravity?'
    _python_name = 'gravity'
    return_type = 'object'

class components(RealVector):
    """
    'components' child.
    """
    _version = '222'
    fluent_name = 'components'
    _python_name = 'components'
    return_type = 'object'

class gravity(Group):
    """
    'gravity' child.
    """
    _version = '222'
    fluent_name = 'gravity'
    _python_name = 'gravity'
    child_names = ['gravity', 'components']
    _child_classes = dict(
        gravity=gravity_1,
        components=components,
    )
    return_type = 'object'

class general(Group):
    """
    'general' child.
    """
    _version = '222'
    fluent_name = 'general'
    _python_name = 'general'
    child_names = ['solver', 'adjust_solver_defaults_based_on_setup', 'gravity']
    _child_classes = dict(
        solver=solver,
        adjust_solver_defaults_based_on_setup=adjust_solver_defaults_based_on_setup,
        gravity=gravity,
    )
    return_type = 'object'

class enabled(Boolean):
    """
    'enabled' child.
    """
    _version = '222'
    fluent_name = 'enabled'
    _python_name = 'enabled'
    return_type = 'object'

class viscous_dissipation(Boolean):
    """
    'viscous_dissipation' child.
    """
    _version = '222'
    fluent_name = 'viscous-dissipation'
    _python_name = 'viscous_dissipation'
    return_type = 'object'

class pressure_work(Boolean):
    """
    'pressure_work' child.
    """
    _version = '222'
    fluent_name = 'pressure-work'
    _python_name = 'pressure_work'
    return_type = 'object'

class kinetic_energy(Boolean):
    """
    'kinetic_energy' child.
    """
    _version = '222'
    fluent_name = 'kinetic-energy'
    _python_name = 'kinetic_energy'
    return_type = 'object'

class inlet_diffusion(Boolean):
    """
    'inlet_diffusion' child.
    """
    _version = '222'
    fluent_name = 'inlet-diffusion'
    _python_name = 'inlet_diffusion'
    return_type = 'object'

class energy(Group):
    """
    'energy' child.
    """
    _version = '222'
    fluent_name = 'energy'
    _python_name = 'energy'
    child_names = ['enabled', 'viscous_dissipation', 'pressure_work', 'kinetic_energy', 'inlet_diffusion']
    _child_classes = dict(
        enabled=enabled,
        viscous_dissipation=viscous_dissipation,
        pressure_work=pressure_work,
        kinetic_energy=kinetic_energy,
        inlet_diffusion=inlet_diffusion,
    )
    return_type = 'object'

class models_1(String, AllowedValuesMixin):
    """
    Multiphase model.
    """
    _version = '222'
    fluent_name = 'models'
    _python_name = 'models'
    return_type = 'object'

class vaporization_pressure(Real):
    """
    Vaporization pressure.
    """
    _version = '222'
    fluent_name = 'vaporization-pressure'
    _python_name = 'vaporization_pressure'
    return_type = 'object'

class non_condensable_gas(Real):
    """
    Non condensable gas.
    """
    _version = '222'
    fluent_name = 'non-condensable-gas'
    _python_name = 'non_condensable_gas'
    return_type = 'object'

class liquid_surface_tension(Real):
    """
    Liquid surface tension.
    """
    _version = '222'
    fluent_name = 'liquid-surface-tension'
    _python_name = 'liquid_surface_tension'
    return_type = 'object'

class bubble_number_density(Real):
    """
    Bubble number density.
    """
    _version = '222'
    fluent_name = 'bubble-number-density'
    _python_name = 'bubble_number_density'
    return_type = 'object'

class number_of_phases(Integer):
    """
    >= 2 and <= 20.
    """
    _version = '222'
    fluent_name = 'number-of-phases'
    _python_name = 'number_of_phases'
    return_type = 'object'

class number_of_eulerian_discrete_phases(IntegerList):
    """
    Sets the number of phases, calculated with the Discrete Phase model.
    The sum of Eulerian and Discrete phases has to be in the range (2,20).
    """
    _version = '222'
    fluent_name = 'number-of-eulerian-discrete-phases'
    _python_name = 'number_of_eulerian_discrete_phases'
    return_type = 'object'

class multiphase(Group):
    """
    'multiphase' child.
    """
    _version = '222'
    fluent_name = 'multiphase'
    _python_name = 'multiphase'
    child_names = ['models', 'vaporization_pressure', 'non_condensable_gas', 'liquid_surface_tension', 'bubble_number_density', 'number_of_phases', 'number_of_eulerian_discrete_phases']
    _child_classes = dict(
        models=models_1,
        vaporization_pressure=vaporization_pressure,
        non_condensable_gas=non_condensable_gas,
        liquid_surface_tension=liquid_surface_tension,
        bubble_number_density=bubble_number_density,
        number_of_phases=number_of_phases,
        number_of_eulerian_discrete_phases=number_of_eulerian_discrete_phases,
    )
    return_type = 'object'

class model(String, AllowedValuesMixin):
    """
    'model' child.
    """
    _version = '222'
    fluent_name = 'model'
    _python_name = 'model'
    return_type = 'object'

class viscous_heating(Boolean):
    """
    Compute viscous energy dissipation.
    """
    _version = '222'
    fluent_name = 'viscous-heating'
    _python_name = 'viscous_heating'
    return_type = 'object'

class low_pressure_slip(Boolean):
    """
    Enable/Disable Low Pressure Boundry Slip.
    """
    _version = '222'
    fluent_name = 'low-pressure-slip?'
    _python_name = 'low_pressure_slip'
    return_type = 'object'

class curvature_correction(Boolean):
    """
    Enable/disable the curvature correction.
    """
    _version = '222'
    fluent_name = 'curvature-correction'
    _python_name = 'curvature_correction'
    return_type = 'object'

class corner_flow_correction(Boolean):
    """
    Enable/disable the corner flow correction.
    """
    _version = '222'
    fluent_name = 'corner-flow-correction'
    _python_name = 'corner_flow_correction'
    return_type = 'object'

class production_kato_launder(Boolean):
    """
    'production_kato_launder' child.
    """
    _version = '222'
    fluent_name = 'production-kato-launder'
    _python_name = 'production_kato_launder'
    return_type = 'object'

class production_limiter(Boolean):
    """
    'production_limiter' child.
    """
    _version = '222'
    fluent_name = 'production-limiter'
    _python_name = 'production_limiter'
    return_type = 'object'

class options(Group):
    """
    'options' child.
    """
    _version = '222'
    fluent_name = 'options'
    _python_name = 'options'
    child_names = ['viscous_heating', 'low_pressure_slip', 'curvature_correction', 'corner_flow_correction', 'production_kato_launder', 'production_limiter']
    _child_classes = dict(
        viscous_heating=viscous_heating,
        low_pressure_slip=low_pressure_slip,
        curvature_correction=curvature_correction,
        corner_flow_correction=corner_flow_correction,
        production_kato_launder=production_kato_launder,
        production_limiter=production_limiter,
    )
    return_type = 'object'

class spalart_allmaras_production(String, AllowedValuesMixin):
    """
    Enable/disable strain/vorticity production in Spalart-Allmaras model.
    """
    _version = '222'
    fluent_name = 'spalart-allmaras-production'
    _python_name = 'spalart_allmaras_production'
    return_type = 'object'

class k_epsilon_model(String, AllowedValuesMixin):
    """
    'k_epsilon_model' child.
    """
    _version = '222'
    fluent_name = 'k-epsilon-model'
    _python_name = 'k_epsilon_model'
    return_type = 'object'

class k_omega_model(String, AllowedValuesMixin):
    """
    'k_omega_model' child.
    """
    _version = '222'
    fluent_name = 'k-omega-model'
    _python_name = 'k_omega_model'
    return_type = 'object'

class kw_low_re_correction(Boolean):
    """
    Enable/disable the k-omega low Re option.
    """
    _version = '222'
    fluent_name = 'kw-low-re-correction'
    _python_name = 'kw_low_re_correction'
    return_type = 'object'

class kw_shear_correction(Boolean):
    """
    Enable/disable the k-omega shear-flow correction option.
    """
    _version = '222'
    fluent_name = 'kw-shear-correction'
    _python_name = 'kw_shear_correction'
    return_type = 'object'

class turb_compressibility(Boolean):
    """
    Enable/disable the compressibility correction option.
    """
    _version = '222'
    fluent_name = 'turb-compressibility'
    _python_name = 'turb_compressibility'
    return_type = 'object'

class k_omega_options(Group):
    """
    'k_omega_options' child.
    """
    _version = '222'
    fluent_name = 'k-omega-options'
    _python_name = 'k_omega_options'
    child_names = ['kw_low_re_correction', 'kw_shear_correction', 'turb_compressibility']
    _child_classes = dict(
        kw_low_re_correction=kw_low_re_correction,
        kw_shear_correction=kw_shear_correction,
        turb_compressibility=turb_compressibility,
    )
    return_type = 'object'

class differential_viscosity_model(Boolean):
    """
    Enable/disable the differential-viscosity model.
    """
    _version = '222'
    fluent_name = 'differential-viscosity-model'
    _python_name = 'differential_viscosity_model'
    return_type = 'object'

class swirl_dominated_flow(Boolean):
    """
    Enable/disable swirl corrections for rng-model.
    """
    _version = '222'
    fluent_name = 'swirl-dominated-flow'
    _python_name = 'swirl_dominated_flow'
    return_type = 'object'

class rng_options(Group):
    """
    'rng_options' child.
    """
    _version = '222'
    fluent_name = 'rng-options'
    _python_name = 'rng_options'
    child_names = ['differential_viscosity_model', 'swirl_dominated_flow']
    _child_classes = dict(
        differential_viscosity_model=differential_viscosity_model,
        swirl_dominated_flow=swirl_dominated_flow,
    )
    return_type = 'object'

class near_wall_treatment(String, AllowedValuesMixin):
    """
    'near_wall_treatment' child.
    """
    _version = '222'
    fluent_name = 'near-wall-treatment'
    _python_name = 'near_wall_treatment'
    return_type = 'object'

class roughness_correlation(Boolean):
    """
    Enable/Disable Transition-SST roughness correlation.
    """
    _version = '222'
    fluent_name = 'roughness-correlation'
    _python_name = 'roughness_correlation'
    return_type = 'object'

class transition_sst_options(Group):
    """
    'transition_sst_options' child.
    """
    _version = '222'
    fluent_name = 'transition-sst-options'
    _python_name = 'transition_sst_options'
    child_names = ['roughness_correlation']
    _child_classes = dict(
        roughness_correlation=roughness_correlation,
    )
    return_type = 'object'

class reynolds_stress_model(String, AllowedValuesMixin):
    """
    'reynolds_stress_model' child.
    """
    _version = '222'
    fluent_name = 'reynolds-stress-model'
    _python_name = 'reynolds_stress_model'
    return_type = 'object'

class subgrid_scale_model(String, AllowedValuesMixin):
    """
    'subgrid_scale_model' child.
    """
    _version = '222'
    fluent_name = 'subgrid-scale-model'
    _python_name = 'subgrid_scale_model'
    return_type = 'object'

class dynamic_stress(Boolean):
    """
    Enable/Disable Dynamic model option.
    """
    _version = '222'
    fluent_name = 'dynamic-stress'
    _python_name = 'dynamic_stress'
    return_type = 'object'

class dynamic_energy_flux(Boolean):
    """
    Enable/disable the dynamic sub-grid scale turbulent Prandtl Number.
    """
    _version = '222'
    fluent_name = 'dynamic-energy-flux'
    _python_name = 'dynamic_energy_flux'
    return_type = 'object'

class dynamic_scalar_flux(Boolean):
    """
    Enable/Disable dynamic Schmidt Number.
    """
    _version = '222'
    fluent_name = 'dynamic-scalar-flux'
    _python_name = 'dynamic_scalar_flux'
    return_type = 'object'

class subgrid_dynamic_fvar(Boolean):
    """
    Enable/Disable the dynamic mixture fraction variance model.
    """
    _version = '222'
    fluent_name = 'subgrid-dynamic-fvar'
    _python_name = 'subgrid_dynamic_fvar'
    return_type = 'object'

class les_model_options(Group):
    """
    'les_model_options' child.
    """
    _version = '222'
    fluent_name = 'les-model-options'
    _python_name = 'les_model_options'
    child_names = ['dynamic_stress', 'dynamic_energy_flux', 'dynamic_scalar_flux', 'subgrid_dynamic_fvar']
    _child_classes = dict(
        dynamic_stress=dynamic_stress,
        dynamic_energy_flux=dynamic_energy_flux,
        dynamic_scalar_flux=dynamic_scalar_flux,
        subgrid_dynamic_fvar=subgrid_dynamic_fvar,
    )
    return_type = 'object'

class solve_tke(Boolean):
    """
    Enable/disable the solution of T.K.E. in RSM model.
    """
    _version = '222'
    fluent_name = 'solve-tke'
    _python_name = 'solve_tke'
    return_type = 'object'

class wall_echo(Boolean):
    """
    Enable/disable wall-echo effects in RSM model.
    """
    _version = '222'
    fluent_name = 'wall-echo'
    _python_name = 'wall_echo'
    return_type = 'object'

class reynolds_stress_options(Group):
    """
    'reynolds_stress_options' child.
    """
    _version = '222'
    fluent_name = 'reynolds-stress-options'
    _python_name = 'reynolds_stress_options'
    child_names = ['solve_tke', 'wall_echo']
    _child_classes = dict(
        solve_tke=solve_tke,
        wall_echo=wall_echo,
    )
    return_type = 'object'

class pressure_gradient_effects(Boolean):
    """
    Enable/disable wall function pressure-gradient effects.
    """
    _version = '222'
    fluent_name = 'pressure-gradient-effects'
    _python_name = 'pressure_gradient_effects'
    return_type = 'object'

class thermal_effects(Boolean):
    """
    Enable/disable wall function thermal effects.
    """
    _version = '222'
    fluent_name = 'thermal-effects'
    _python_name = 'thermal_effects'
    return_type = 'object'

class enhanced_wall_treatment_options(Group):
    """
    'enhanced_wall_treatment_options' child.
    """
    _version = '222'
    fluent_name = 'enhanced-wall-treatment-options'
    _python_name = 'enhanced_wall_treatment_options'
    child_names = ['pressure_gradient_effects', 'thermal_effects']
    _child_classes = dict(
        pressure_gradient_effects=pressure_gradient_effects,
        thermal_effects=thermal_effects,
    )
    return_type = 'object'

class rans_model(String, AllowedValuesMixin):
    """
    'rans_model' child.
    """
    _version = '222'
    fluent_name = 'rans-model'
    _python_name = 'rans_model'
    return_type = 'object'

class viscous(Group):
    """
    'viscous' child.
    """
    _version = '222'
    fluent_name = 'viscous'
    _python_name = 'viscous'
    child_names = ['model', 'options', 'spalart_allmaras_production', 'k_epsilon_model', 'k_omega_model', 'k_omega_options', 'rng_options', 'near_wall_treatment', 'transition_sst_options', 'reynolds_stress_model', 'subgrid_scale_model', 'les_model_options', 'reynolds_stress_options', 'enhanced_wall_treatment_options', 'rans_model']
    _child_classes = dict(
        model=model,
        options=options,
        spalart_allmaras_production=spalart_allmaras_production,
        k_epsilon_model=k_epsilon_model,
        k_omega_model=k_omega_model,
        k_omega_options=k_omega_options,
        rng_options=rng_options,
        near_wall_treatment=near_wall_treatment,
        transition_sst_options=transition_sst_options,
        reynolds_stress_model=reynolds_stress_model,
        subgrid_scale_model=subgrid_scale_model,
        les_model_options=les_model_options,
        reynolds_stress_options=reynolds_stress_options,
        enhanced_wall_treatment_options=enhanced_wall_treatment_options,
        rans_model=rans_model,
    )
    return_type = 'object'

class models(Group):
    """
    'models' child.
    """
    _version = '222'
    fluent_name = 'models'
    _python_name = 'models'
    child_names = ['energy', 'multiphase', 'viscous']
    _child_classes = dict(
        energy=energy,
        multiphase=multiphase,
        viscous=viscous,
    )
    return_type = 'object'

class option(String, AllowedValuesMixin):
    """
    'option' child.
    """
    _version = '222'
    fluent_name = 'option'
    _python_name = 'option'
    return_type = 'object'

class constant(Real):
    """
    'constant' child.
    """
    _version = '222'
    fluent_name = 'constant'
    _python_name = 'constant'
    return_type = 'object'

class boussinesq(Real):
    """
    'boussinesq' child.
    """
    _version = '222'
    fluent_name = 'boussinesq'
    _python_name = 'boussinesq'
    return_type = 'object'

class coefficients(RealList):
    """
    'coefficients' child.
    """
    _version = '222'
    fluent_name = 'coefficients'
    _python_name = 'coefficients'
    return_type = 'object'

class number_of_coefficients(Integer):
    """
    'number_of_coefficients' child.
    """
    _version = '222'
    fluent_name = 'number-of-coefficients'
    _python_name = 'number_of_coefficients'
    return_type = 'object'

class minimum(Real):
    """
    'minimum' child.
    """
    _version = '222'
    fluent_name = 'minimum'
    _python_name = 'minimum'
    return_type = 'object'

class maximum(Real):
    """
    'maximum' child.
    """
    _version = '222'
    fluent_name = 'maximum'
    _python_name = 'maximum'
    return_type = 'object'

class number_of_coeff(Integer):
    """
    'number_of_coeff' child.
    """
    _version = '222'
    fluent_name = 'number-of-coeff'
    _python_name = 'number_of_coeff'
    return_type = 'object'

class piecewise_polynomial_child(Group):
    """
    'child_object_type' of piecewise_polynomial.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'piecewise_polynomial_child'
    child_names = ['minimum', 'maximum', 'number_of_coeff', 'coefficients']
    _child_classes = dict(
        minimum=minimum,
        maximum=maximum,
        number_of_coeff=number_of_coeff,
        coefficients=coefficients,
    )
    return_type = 'object'

class piecewise_polynomial(ListObject[piecewise_polynomial_child]):
    """
    'piecewise_polynomial' child.
    """
    _version = '222'
    fluent_name = 'piecewise-polynomial'
    _python_name = 'piecewise_polynomial'
    child_object_type = piecewise_polynomial_child
    return_type = 'object'

class nasa_9_piecewise_polynomial_child(Group):
    """
    'child_object_type' of nasa_9_piecewise_polynomial.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'nasa_9_piecewise_polynomial_child'
    child_names = ['minimum', 'maximum', 'number_of_coeff', 'coefficients']
    _child_classes = dict(
        minimum=minimum,
        maximum=maximum,
        number_of_coeff=number_of_coeff,
        coefficients=coefficients,
    )
    return_type = 'object'

class nasa_9_piecewise_polynomial(ListObject[nasa_9_piecewise_polynomial_child]):
    """
    'nasa_9_piecewise_polynomial' child.
    """
    _version = '222'
    fluent_name = 'nasa-9-piecewise-polynomial'
    _python_name = 'nasa_9_piecewise_polynomial'
    child_object_type = nasa_9_piecewise_polynomial_child
    return_type = 'object'

class piecewise_linear_child(RealList):
    """
    'child_object_type' of piecewise_linear.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'piecewise_linear_child'
    return_type = 'object'

class piecewise_linear(ListObject[piecewise_linear_child]):
    """
    'piecewise_linear' child.
    """
    _version = '222'
    fluent_name = 'piecewise-linear'
    _python_name = 'piecewise_linear'
    child_object_type = piecewise_linear_child
    return_type = 'object'

class matrix_component(RealList):
    """
    'matrix_component' child.
    """
    _version = '222'
    fluent_name = 'matrix-component'
    _python_name = 'matrix_component'
    return_type = 'object'

class conductivity(Group):
    """
    'conductivity' child.
    """
    _version = '222'
    fluent_name = 'conductivity'
    _python_name = 'conductivity'
    child_names = ['option', 'constant', 'coefficients', 'number_of_coefficients', 'piecewise_linear', 'piecewise_polynomial']
    _child_classes = dict(
        option=option,
        constant=constant,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_linear=piecewise_linear,
        piecewise_polynomial=piecewise_polynomial,
    )
    return_type = 'object'

class anisotropic(Group):
    """
    'anisotropic' child.
    """
    _version = '222'
    fluent_name = 'anisotropic'
    _python_name = 'anisotropic'
    child_names = ['matrix_component', 'conductivity']
    _child_classes = dict(
        matrix_component=matrix_component,
        conductivity=conductivity,
    )
    return_type = 'object'

class direction_0(RealList):
    """
    'direction_0' child.
    """
    _version = '222'
    fluent_name = 'direction-0'
    _python_name = 'direction_0'
    return_type = 'object'

class direction_1(RealList):
    """
    'direction_1' child.
    """
    _version = '222'
    fluent_name = 'direction-1'
    _python_name = 'direction_1'
    return_type = 'object'

class conductivity_0(Group):
    """
    'conductivity_0' child.
    """
    _version = '222'
    fluent_name = 'conductivity-0'
    _python_name = 'conductivity_0'
    child_names = ['option', 'constant', 'coefficients', 'number_of_coefficients', 'piecewise_linear', 'piecewise_polynomial']
    _child_classes = dict(
        option=option,
        constant=constant,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_linear=piecewise_linear,
        piecewise_polynomial=piecewise_polynomial,
    )
    return_type = 'object'

class conductivity_1(Group):
    """
    'conductivity_1' child.
    """
    _version = '222'
    fluent_name = 'conductivity-1'
    _python_name = 'conductivity_1'
    child_names = ['option', 'constant', 'coefficients', 'number_of_coefficients', 'piecewise_linear', 'piecewise_polynomial']
    _child_classes = dict(
        option=option,
        constant=constant,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_linear=piecewise_linear,
        piecewise_polynomial=piecewise_polynomial,
    )
    return_type = 'object'

class conductivity_2(Group):
    """
    'conductivity_2' child.
    """
    _version = '222'
    fluent_name = 'conductivity-2'
    _python_name = 'conductivity_2'
    child_names = ['option', 'constant', 'coefficients', 'number_of_coefficients', 'piecewise_linear', 'piecewise_polynomial']
    _child_classes = dict(
        option=option,
        constant=constant,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_linear=piecewise_linear,
        piecewise_polynomial=piecewise_polynomial,
    )
    return_type = 'object'

class orthotropic(Group):
    """
    'orthotropic' child.
    """
    _version = '222'
    fluent_name = 'orthotropic'
    _python_name = 'orthotropic'
    child_names = ['direction_0', 'direction_1', 'conductivity_0', 'conductivity_1', 'conductivity_2']
    _child_classes = dict(
        direction_0=direction_0,
        direction_1=direction_1,
        conductivity_0=conductivity_0,
        conductivity_1=conductivity_1,
        conductivity_2=conductivity_2,
    )
    return_type = 'object'

class var_class(String):
    """
    'var_class' child.
    """
    _version = '222'
    fluent_name = 'var-class'
    _python_name = 'var_class'
    return_type = 'object'

class species(Group):
    """
    'species' child.
    """
    _version = '222'
    fluent_name = 'species'
    _python_name = 'species'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class reactions(Group):
    """
    'reactions' child.
    """
    _version = '222'
    fluent_name = 'reactions'
    _python_name = 'reactions'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class reaction_mechs(Group):
    """
    'reaction_mechs' child.
    """
    _version = '222'
    fluent_name = 'reaction-mechs'
    _python_name = 'reaction_mechs'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class density(Group):
    """
    'density' child.
    """
    _version = '222'
    fluent_name = 'density'
    _python_name = 'density'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class specific_heat(Group):
    """
    'specific_heat' child.
    """
    _version = '222'
    fluent_name = 'specific-heat'
    _python_name = 'specific_heat'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class thermal_conductivity(Group):
    """
    'thermal_conductivity' child.
    """
    _version = '222'
    fluent_name = 'thermal-conductivity'
    _python_name = 'thermal_conductivity'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class viscosity(Group):
    """
    'viscosity' child.
    """
    _version = '222'
    fluent_name = 'viscosity'
    _python_name = 'viscosity'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class molecular_weight(Group):
    """
    'molecular_weight' child.
    """
    _version = '222'
    fluent_name = 'molecular-weight'
    _python_name = 'molecular_weight'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class mass_diffusivity(Group):
    """
    'mass_diffusivity' child.
    """
    _version = '222'
    fluent_name = 'mass-diffusivity'
    _python_name = 'mass_diffusivity'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class thermal_diffusivity(Group):
    """
    'thermal_diffusivity' child.
    """
    _version = '222'
    fluent_name = 'thermal-diffusivity'
    _python_name = 'thermal_diffusivity'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class formation_enthalpy(Group):
    """
    'formation_enthalpy' child.
    """
    _version = '222'
    fluent_name = 'formation-enthalpy'
    _python_name = 'formation_enthalpy'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class formation_entropy(Group):
    """
    'formation_entropy' child.
    """
    _version = '222'
    fluent_name = 'formation-entropy'
    _python_name = 'formation_entropy'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class characteristic_vibrational_temperature(Group):
    """
    'characteristic_vibrational_temperature' child.
    """
    _version = '222'
    fluent_name = 'characteristic-vibrational-temperature'
    _python_name = 'characteristic_vibrational_temperature'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class reference_temperature(Group):
    """
    'reference_temperature' child.
    """
    _version = '222'
    fluent_name = 'reference-temperature'
    _python_name = 'reference_temperature'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class lennard_jones_length(Group):
    """
    'lennard_jones_length' child.
    """
    _version = '222'
    fluent_name = 'lennard-jones-length'
    _python_name = 'lennard_jones_length'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class lennard_jones_energy(Group):
    """
    'lennard_jones_energy' child.
    """
    _version = '222'
    fluent_name = 'lennard-jones-energy'
    _python_name = 'lennard_jones_energy'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class thermal_accom_coefficient(Group):
    """
    'thermal_accom_coefficient' child.
    """
    _version = '222'
    fluent_name = 'thermal-accom-coefficient'
    _python_name = 'thermal_accom_coefficient'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class velocity_accom_coefficient(Group):
    """
    'velocity_accom_coefficient' child.
    """
    _version = '222'
    fluent_name = 'velocity-accom-coefficient'
    _python_name = 'velocity_accom_coefficient'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class absorption_coefficient(Group):
    """
    'absorption_coefficient' child.
    """
    _version = '222'
    fluent_name = 'absorption-coefficient'
    _python_name = 'absorption_coefficient'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class scattering_coefficient(Group):
    """
    'scattering_coefficient' child.
    """
    _version = '222'
    fluent_name = 'scattering-coefficient'
    _python_name = 'scattering_coefficient'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class scattering_phase_function(Group):
    """
    'scattering_phase_function' child.
    """
    _version = '222'
    fluent_name = 'scattering-phase-function'
    _python_name = 'scattering_phase_function'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class therm_exp_coeff(Group):
    """
    'therm_exp_coeff' child.
    """
    _version = '222'
    fluent_name = 'therm-exp-coeff'
    _python_name = 'therm_exp_coeff'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class premix_unburnt_density(Group):
    """
    'premix_unburnt_density' child.
    """
    _version = '222'
    fluent_name = 'premix-unburnt-density'
    _python_name = 'premix_unburnt_density'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class premix_unburnt_temp(Group):
    """
    'premix_unburnt_temp' child.
    """
    _version = '222'
    fluent_name = 'premix-unburnt-temp'
    _python_name = 'premix_unburnt_temp'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class premix_adiabatic_temp(Group):
    """
    'premix_adiabatic_temp' child.
    """
    _version = '222'
    fluent_name = 'premix-adiabatic-temp'
    _python_name = 'premix_adiabatic_temp'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class premix_unburnt_cp(Group):
    """
    'premix_unburnt_cp' child.
    """
    _version = '222'
    fluent_name = 'premix-unburnt-cp'
    _python_name = 'premix_unburnt_cp'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class premix_heat_trans_coeff(Group):
    """
    'premix_heat_trans_coeff' child.
    """
    _version = '222'
    fluent_name = 'premix-heat-trans-coeff'
    _python_name = 'premix_heat_trans_coeff'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class premix_laminar_speed(Group):
    """
    'premix_laminar_speed' child.
    """
    _version = '222'
    fluent_name = 'premix-laminar-speed'
    _python_name = 'premix_laminar_speed'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class premix_laminar_thickness(Group):
    """
    'premix_laminar_thickness' child.
    """
    _version = '222'
    fluent_name = 'premix-laminar-thickness'
    _python_name = 'premix_laminar_thickness'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class premix_critical_strain(Group):
    """
    'premix_critical_strain' child.
    """
    _version = '222'
    fluent_name = 'premix-critical-strain'
    _python_name = 'premix_critical_strain'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class premix_heat_of_comb(Group):
    """
    'premix_heat_of_comb' child.
    """
    _version = '222'
    fluent_name = 'premix-heat-of-comb'
    _python_name = 'premix_heat_of_comb'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class premix_unburnt_fuel_mf(Group):
    """
    'premix_unburnt_fuel_mf' child.
    """
    _version = '222'
    fluent_name = 'premix-unburnt-fuel-mf'
    _python_name = 'premix_unburnt_fuel_mf'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class refractive_index(Group):
    """
    'refractive_index' child.
    """
    _version = '222'
    fluent_name = 'refractive-index'
    _python_name = 'refractive_index'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class latent_heat(Group):
    """
    'latent_heat' child.
    """
    _version = '222'
    fluent_name = 'latent-heat'
    _python_name = 'latent_heat'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class thermophoretic_co(Group):
    """
    'thermophoretic_co' child.
    """
    _version = '222'
    fluent_name = 'thermophoretic-co'
    _python_name = 'thermophoretic_co'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class vaporization_temperature(Group):
    """
    'vaporization_temperature' child.
    """
    _version = '222'
    fluent_name = 'vaporization-temperature'
    _python_name = 'vaporization_temperature'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class boiling_point(Group):
    """
    'boiling_point' child.
    """
    _version = '222'
    fluent_name = 'boiling-point'
    _python_name = 'boiling_point'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class volatile_fraction(Group):
    """
    'volatile_fraction' child.
    """
    _version = '222'
    fluent_name = 'volatile-fraction'
    _python_name = 'volatile_fraction'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class binary_diffusivity(Group):
    """
    'binary_diffusivity' child.
    """
    _version = '222'
    fluent_name = 'binary-diffusivity'
    _python_name = 'binary_diffusivity'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class diffusivity_reference_pressure(Group):
    """
    'diffusivity_reference_pressure' child.
    """
    _version = '222'
    fluent_name = 'diffusivity-reference-pressure'
    _python_name = 'diffusivity_reference_pressure'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class vapor_pressure(Group):
    """
    'vapor_pressure' child.
    """
    _version = '222'
    fluent_name = 'vapor-pressure'
    _python_name = 'vapor_pressure'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class degrees_of_freedom(Group):
    """
    'degrees_of_freedom' child.
    """
    _version = '222'
    fluent_name = 'degrees-of-freedom'
    _python_name = 'degrees_of_freedom'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class emissivity(Group):
    """
    'emissivity' child.
    """
    _version = '222'
    fluent_name = 'emissivity'
    _python_name = 'emissivity'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class scattering_factor(Group):
    """
    'scattering_factor' child.
    """
    _version = '222'
    fluent_name = 'scattering-factor'
    _python_name = 'scattering_factor'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class heat_of_pyrolysis(Group):
    """
    'heat_of_pyrolysis' child.
    """
    _version = '222'
    fluent_name = 'heat-of-pyrolysis'
    _python_name = 'heat_of_pyrolysis'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class swelling_coefficient(Group):
    """
    'swelling_coefficient' child.
    """
    _version = '222'
    fluent_name = 'swelling-coefficient'
    _python_name = 'swelling_coefficient'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class burn_stoichiometry(Group):
    """
    'burn_stoichiometry' child.
    """
    _version = '222'
    fluent_name = 'burn-stoichiometry'
    _python_name = 'burn_stoichiometry'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class combustible_fraction(Group):
    """
    'combustible_fraction' child.
    """
    _version = '222'
    fluent_name = 'combustible-fraction'
    _python_name = 'combustible_fraction'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class burn_hreact(Group):
    """
    'burn_hreact' child.
    """
    _version = '222'
    fluent_name = 'burn-hreact'
    _python_name = 'burn_hreact'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class burn_hreact_fraction(Group):
    """
    'burn_hreact_fraction' child.
    """
    _version = '222'
    fluent_name = 'burn-hreact-fraction'
    _python_name = 'burn_hreact_fraction'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class devolatilization_model(Group):
    """
    'devolatilization_model' child.
    """
    _version = '222'
    fluent_name = 'devolatilization-model'
    _python_name = 'devolatilization_model'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class combustion_model(Group):
    """
    'combustion_model' child.
    """
    _version = '222'
    fluent_name = 'combustion-model'
    _python_name = 'combustion_model'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class averaging_coefficient_t(Group):
    """
    'averaging_coefficient_t' child.
    """
    _version = '222'
    fluent_name = 'averaging-coefficient-t'
    _python_name = 'averaging_coefficient_t'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class averaging_coefficient_y(Group):
    """
    'averaging_coefficient_y' child.
    """
    _version = '222'
    fluent_name = 'averaging-coefficient-y'
    _python_name = 'averaging_coefficient_y'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class vaporization_model(Group):
    """
    'vaporization_model' child.
    """
    _version = '222'
    fluent_name = 'vaporization-model'
    _python_name = 'vaporization_model'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class thermolysis_model(Group):
    """
    'thermolysis_model' child.
    """
    _version = '222'
    fluent_name = 'thermolysis-model'
    _python_name = 'thermolysis_model'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class melting_heat(Group):
    """
    'melting_heat' child.
    """
    _version = '222'
    fluent_name = 'melting-heat'
    _python_name = 'melting_heat'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class tsolidus(Group):
    """
    'tsolidus' child.
    """
    _version = '222'
    fluent_name = 'tsolidus'
    _python_name = 'tsolidus'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class tliqidus(Group):
    """
    'tliqidus' child.
    """
    _version = '222'
    fluent_name = 'tliqidus'
    _python_name = 'tliqidus'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class tmelt(Group):
    """
    'tmelt' child.
    """
    _version = '222'
    fluent_name = 'tmelt'
    _python_name = 'tmelt'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class liquidus_slope(Group):
    """
    'liquidus_slope' child.
    """
    _version = '222'
    fluent_name = 'liquidus-slope'
    _python_name = 'liquidus_slope'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class partition_coeff(Group):
    """
    'partition_coeff' child.
    """
    _version = '222'
    fluent_name = 'partition-coeff'
    _python_name = 'partition_coeff'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class eutectic_mf(Group):
    """
    'eutectic_mf' child.
    """
    _version = '222'
    fluent_name = 'eutectic-mf'
    _python_name = 'eutectic_mf'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class eutectic_temp(Group):
    """
    'eutectic_temp' child.
    """
    _version = '222'
    fluent_name = 'eutectic-temp'
    _python_name = 'eutectic_temp'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class solut_exp_coeff(Group):
    """
    'solut_exp_coeff' child.
    """
    _version = '222'
    fluent_name = 'solut-exp-coeff'
    _python_name = 'solut_exp_coeff'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class solid_diffusion(Group):
    """
    'solid_diffusion' child.
    """
    _version = '222'
    fluent_name = 'solid-diffusion'
    _python_name = 'solid_diffusion'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class uds_diffusivity(Group):
    """
    'uds_diffusivity' child.
    """
    _version = '222'
    fluent_name = 'uds-diffusivity'
    _python_name = 'uds_diffusivity'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class dpm_surften(Group):
    """
    'dpm_surften' child.
    """
    _version = '222'
    fluent_name = 'dpm-surften'
    _python_name = 'dpm_surften'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class electric_conductivity(Group):
    """
    'electric_conductivity' child.
    """
    _version = '222'
    fluent_name = 'electric-conductivity'
    _python_name = 'electric_conductivity'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class dual_electric_conductivity(Group):
    """
    'dual_electric_conductivity' child.
    """
    _version = '222'
    fluent_name = 'dual-electric-conductivity'
    _python_name = 'dual_electric_conductivity'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class lithium_diffusivity(Group):
    """
    'lithium_diffusivity' child.
    """
    _version = '222'
    fluent_name = 'lithium-diffusivity'
    _python_name = 'lithium_diffusivity'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class magnetic_permeability(Group):
    """
    'magnetic_permeability' child.
    """
    _version = '222'
    fluent_name = 'magnetic-permeability'
    _python_name = 'magnetic_permeability'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class charge_density(Group):
    """
    'charge_density' child.
    """
    _version = '222'
    fluent_name = 'charge-density'
    _python_name = 'charge_density'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class charge(Group):
    """
    'charge' child.
    """
    _version = '222'
    fluent_name = 'charge'
    _python_name = 'charge'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class speed_of_sound(Group):
    """
    'speed_of_sound' child.
    """
    _version = '222'
    fluent_name = 'speed-of-sound'
    _python_name = 'speed_of_sound'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class species_phase(Group):
    """
    'species_phase' child.
    """
    _version = '222'
    fluent_name = 'species-phase'
    _python_name = 'species_phase'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class vp_equilib(Group):
    """
    'vp_equilib' child.
    """
    _version = '222'
    fluent_name = 'vp-equilib'
    _python_name = 'vp_equilib'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class critical_temperature(Group):
    """
    'critical_temperature' child.
    """
    _version = '222'
    fluent_name = 'critical-temperature'
    _python_name = 'critical_temperature'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class critical_pressure(Group):
    """
    'critical_pressure' child.
    """
    _version = '222'
    fluent_name = 'critical-pressure'
    _python_name = 'critical_pressure'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class critical_volume(Group):
    """
    'critical_volume' child.
    """
    _version = '222'
    fluent_name = 'critical-volume'
    _python_name = 'critical_volume'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class acentric_factor(Group):
    """
    'acentric_factor' child.
    """
    _version = '222'
    fluent_name = 'acentric-factor'
    _python_name = 'acentric_factor'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class saturation_pressure(Group):
    """
    'saturation_pressure' child.
    """
    _version = '222'
    fluent_name = 'saturation-pressure'
    _python_name = 'saturation_pressure'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class struct_youngs_modulus(Group):
    """
    'struct_youngs_modulus' child.
    """
    _version = '222'
    fluent_name = 'struct-youngs-modulus'
    _python_name = 'struct_youngs_modulus'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class struct_poisson_ratio(Group):
    """
    'struct_poisson_ratio' child.
    """
    _version = '222'
    fluent_name = 'struct-poisson-ratio'
    _python_name = 'struct_poisson_ratio'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class struct_start_temperature(Group):
    """
    'struct_start_temperature' child.
    """
    _version = '222'
    fluent_name = 'struct-start-temperature'
    _python_name = 'struct_start_temperature'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class struct_thermal_expansion(Group):
    """
    'struct_thermal_expansion' child.
    """
    _version = '222'
    fluent_name = 'struct-thermal-expansion'
    _python_name = 'struct_thermal_expansion'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class atomic_number(Group):
    """
    'atomic_number' child.
    """
    _version = '222'
    fluent_name = 'atomic-number'
    _python_name = 'atomic_number'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class struct_damping_alpha(Group):
    """
    'struct_damping_alpha' child.
    """
    _version = '222'
    fluent_name = 'struct-damping-alpha'
    _python_name = 'struct_damping_alpha'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class struct_damping_beta(Group):
    """
    'struct_damping_beta' child.
    """
    _version = '222'
    fluent_name = 'struct-damping-beta'
    _python_name = 'struct_damping_beta'
    child_names = ['option', 'constant', 'boussinesq', 'coefficients', 'number_of_coefficients', 'piecewise_polynomial', 'nasa_9_piecewise_polynomial', 'piecewise_linear', 'anisotropic', 'orthotropic', 'var_class']
    _child_classes = dict(
        option=option,
        constant=constant,
        boussinesq=boussinesq,
        coefficients=coefficients,
        number_of_coefficients=number_of_coefficients,
        piecewise_polynomial=piecewise_polynomial,
        nasa_9_piecewise_polynomial=nasa_9_piecewise_polynomial,
        piecewise_linear=piecewise_linear,
        anisotropic=anisotropic,
        orthotropic=orthotropic,
        var_class=var_class,
    )
    return_type = 'object'

class fluid_child(Group):
    """
    'child_object_type' of fluid.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'fluid_child'
    child_names = ['species', 'reactions', 'reaction_mechs', 'density', 'specific_heat', 'thermal_conductivity', 'viscosity', 'molecular_weight', 'mass_diffusivity', 'thermal_diffusivity', 'formation_enthalpy', 'formation_entropy', 'characteristic_vibrational_temperature', 'reference_temperature', 'lennard_jones_length', 'lennard_jones_energy', 'thermal_accom_coefficient', 'velocity_accom_coefficient', 'absorption_coefficient', 'scattering_coefficient', 'scattering_phase_function', 'therm_exp_coeff', 'premix_unburnt_density', 'premix_unburnt_temp', 'premix_adiabatic_temp', 'premix_unburnt_cp', 'premix_heat_trans_coeff', 'premix_laminar_speed', 'premix_laminar_thickness', 'premix_critical_strain', 'premix_heat_of_comb', 'premix_unburnt_fuel_mf', 'refractive_index', 'latent_heat', 'thermophoretic_co', 'vaporization_temperature', 'boiling_point', 'volatile_fraction', 'binary_diffusivity', 'diffusivity_reference_pressure', 'vapor_pressure', 'degrees_of_freedom', 'emissivity', 'scattering_factor', 'heat_of_pyrolysis', 'swelling_coefficient', 'burn_stoichiometry', 'combustible_fraction', 'burn_hreact', 'burn_hreact_fraction', 'devolatilization_model', 'combustion_model', 'averaging_coefficient_t', 'averaging_coefficient_y', 'vaporization_model', 'thermolysis_model', 'melting_heat', 'tsolidus', 'tliqidus', 'tmelt', 'liquidus_slope', 'partition_coeff', 'eutectic_mf', 'eutectic_temp', 'solut_exp_coeff', 'solid_diffusion', 'uds_diffusivity', 'dpm_surften', 'electric_conductivity', 'dual_electric_conductivity', 'lithium_diffusivity', 'magnetic_permeability', 'charge_density', 'charge', 'speed_of_sound', 'species_phase', 'vp_equilib', 'critical_temperature', 'critical_pressure', 'critical_volume', 'acentric_factor', 'saturation_pressure', 'struct_youngs_modulus', 'struct_poisson_ratio', 'struct_start_temperature', 'struct_thermal_expansion', 'atomic_number', 'struct_damping_alpha', 'struct_damping_beta']
    _child_classes = dict(
        species=species,
        reactions=reactions,
        reaction_mechs=reaction_mechs,
        density=density,
        specific_heat=specific_heat,
        thermal_conductivity=thermal_conductivity,
        viscosity=viscosity,
        molecular_weight=molecular_weight,
        mass_diffusivity=mass_diffusivity,
        thermal_diffusivity=thermal_diffusivity,
        formation_enthalpy=formation_enthalpy,
        formation_entropy=formation_entropy,
        characteristic_vibrational_temperature=characteristic_vibrational_temperature,
        reference_temperature=reference_temperature,
        lennard_jones_length=lennard_jones_length,
        lennard_jones_energy=lennard_jones_energy,
        thermal_accom_coefficient=thermal_accom_coefficient,
        velocity_accom_coefficient=velocity_accom_coefficient,
        absorption_coefficient=absorption_coefficient,
        scattering_coefficient=scattering_coefficient,
        scattering_phase_function=scattering_phase_function,
        therm_exp_coeff=therm_exp_coeff,
        premix_unburnt_density=premix_unburnt_density,
        premix_unburnt_temp=premix_unburnt_temp,
        premix_adiabatic_temp=premix_adiabatic_temp,
        premix_unburnt_cp=premix_unburnt_cp,
        premix_heat_trans_coeff=premix_heat_trans_coeff,
        premix_laminar_speed=premix_laminar_speed,
        premix_laminar_thickness=premix_laminar_thickness,
        premix_critical_strain=premix_critical_strain,
        premix_heat_of_comb=premix_heat_of_comb,
        premix_unburnt_fuel_mf=premix_unburnt_fuel_mf,
        refractive_index=refractive_index,
        latent_heat=latent_heat,
        thermophoretic_co=thermophoretic_co,
        vaporization_temperature=vaporization_temperature,
        boiling_point=boiling_point,
        volatile_fraction=volatile_fraction,
        binary_diffusivity=binary_diffusivity,
        diffusivity_reference_pressure=diffusivity_reference_pressure,
        vapor_pressure=vapor_pressure,
        degrees_of_freedom=degrees_of_freedom,
        emissivity=emissivity,
        scattering_factor=scattering_factor,
        heat_of_pyrolysis=heat_of_pyrolysis,
        swelling_coefficient=swelling_coefficient,
        burn_stoichiometry=burn_stoichiometry,
        combustible_fraction=combustible_fraction,
        burn_hreact=burn_hreact,
        burn_hreact_fraction=burn_hreact_fraction,
        devolatilization_model=devolatilization_model,
        combustion_model=combustion_model,
        averaging_coefficient_t=averaging_coefficient_t,
        averaging_coefficient_y=averaging_coefficient_y,
        vaporization_model=vaporization_model,
        thermolysis_model=thermolysis_model,
        melting_heat=melting_heat,
        tsolidus=tsolidus,
        tliqidus=tliqidus,
        tmelt=tmelt,
        liquidus_slope=liquidus_slope,
        partition_coeff=partition_coeff,
        eutectic_mf=eutectic_mf,
        eutectic_temp=eutectic_temp,
        solut_exp_coeff=solut_exp_coeff,
        solid_diffusion=solid_diffusion,
        uds_diffusivity=uds_diffusivity,
        dpm_surften=dpm_surften,
        electric_conductivity=electric_conductivity,
        dual_electric_conductivity=dual_electric_conductivity,
        lithium_diffusivity=lithium_diffusivity,
        magnetic_permeability=magnetic_permeability,
        charge_density=charge_density,
        charge=charge,
        speed_of_sound=speed_of_sound,
        species_phase=species_phase,
        vp_equilib=vp_equilib,
        critical_temperature=critical_temperature,
        critical_pressure=critical_pressure,
        critical_volume=critical_volume,
        acentric_factor=acentric_factor,
        saturation_pressure=saturation_pressure,
        struct_youngs_modulus=struct_youngs_modulus,
        struct_poisson_ratio=struct_poisson_ratio,
        struct_start_temperature=struct_start_temperature,
        struct_thermal_expansion=struct_thermal_expansion,
        atomic_number=atomic_number,
        struct_damping_alpha=struct_damping_alpha,
        struct_damping_beta=struct_damping_beta,
    )
    return_type = 'object'

class fluid(NamedObject[fluid_child], CreatableNamedObjectMixinOld[fluid_child]):
    """
    'fluid' child.
    """
    _version = '222'
    fluent_name = 'fluid'
    _python_name = 'fluid'
    child_object_type = fluid_child
    return_type = 'object'

class solid_child(Group):
    """
    'child_object_type' of solid.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'solid_child'
    child_names = ['species', 'reactions', 'reaction_mechs', 'density', 'specific_heat', 'thermal_conductivity', 'viscosity', 'molecular_weight', 'mass_diffusivity', 'thermal_diffusivity', 'formation_enthalpy', 'formation_entropy', 'characteristic_vibrational_temperature', 'reference_temperature', 'lennard_jones_length', 'lennard_jones_energy', 'thermal_accom_coefficient', 'velocity_accom_coefficient', 'absorption_coefficient', 'scattering_coefficient', 'scattering_phase_function', 'therm_exp_coeff', 'premix_unburnt_density', 'premix_unburnt_temp', 'premix_adiabatic_temp', 'premix_unburnt_cp', 'premix_heat_trans_coeff', 'premix_laminar_speed', 'premix_laminar_thickness', 'premix_critical_strain', 'premix_heat_of_comb', 'premix_unburnt_fuel_mf', 'refractive_index', 'latent_heat', 'thermophoretic_co', 'vaporization_temperature', 'boiling_point', 'volatile_fraction', 'binary_diffusivity', 'diffusivity_reference_pressure', 'vapor_pressure', 'degrees_of_freedom', 'emissivity', 'scattering_factor', 'heat_of_pyrolysis', 'swelling_coefficient', 'burn_stoichiometry', 'combustible_fraction', 'burn_hreact', 'burn_hreact_fraction', 'devolatilization_model', 'combustion_model', 'averaging_coefficient_t', 'averaging_coefficient_y', 'vaporization_model', 'thermolysis_model', 'melting_heat', 'tsolidus', 'tliqidus', 'tmelt', 'liquidus_slope', 'partition_coeff', 'eutectic_mf', 'eutectic_temp', 'solut_exp_coeff', 'solid_diffusion', 'uds_diffusivity', 'dpm_surften', 'electric_conductivity', 'dual_electric_conductivity', 'lithium_diffusivity', 'magnetic_permeability', 'charge_density', 'charge', 'speed_of_sound', 'species_phase', 'vp_equilib', 'critical_temperature', 'critical_pressure', 'critical_volume', 'acentric_factor', 'saturation_pressure', 'struct_youngs_modulus', 'struct_poisson_ratio', 'struct_start_temperature', 'struct_thermal_expansion', 'atomic_number', 'struct_damping_alpha', 'struct_damping_beta']
    _child_classes = dict(
        species=species,
        reactions=reactions,
        reaction_mechs=reaction_mechs,
        density=density,
        specific_heat=specific_heat,
        thermal_conductivity=thermal_conductivity,
        viscosity=viscosity,
        molecular_weight=molecular_weight,
        mass_diffusivity=mass_diffusivity,
        thermal_diffusivity=thermal_diffusivity,
        formation_enthalpy=formation_enthalpy,
        formation_entropy=formation_entropy,
        characteristic_vibrational_temperature=characteristic_vibrational_temperature,
        reference_temperature=reference_temperature,
        lennard_jones_length=lennard_jones_length,
        lennard_jones_energy=lennard_jones_energy,
        thermal_accom_coefficient=thermal_accom_coefficient,
        velocity_accom_coefficient=velocity_accom_coefficient,
        absorption_coefficient=absorption_coefficient,
        scattering_coefficient=scattering_coefficient,
        scattering_phase_function=scattering_phase_function,
        therm_exp_coeff=therm_exp_coeff,
        premix_unburnt_density=premix_unburnt_density,
        premix_unburnt_temp=premix_unburnt_temp,
        premix_adiabatic_temp=premix_adiabatic_temp,
        premix_unburnt_cp=premix_unburnt_cp,
        premix_heat_trans_coeff=premix_heat_trans_coeff,
        premix_laminar_speed=premix_laminar_speed,
        premix_laminar_thickness=premix_laminar_thickness,
        premix_critical_strain=premix_critical_strain,
        premix_heat_of_comb=premix_heat_of_comb,
        premix_unburnt_fuel_mf=premix_unburnt_fuel_mf,
        refractive_index=refractive_index,
        latent_heat=latent_heat,
        thermophoretic_co=thermophoretic_co,
        vaporization_temperature=vaporization_temperature,
        boiling_point=boiling_point,
        volatile_fraction=volatile_fraction,
        binary_diffusivity=binary_diffusivity,
        diffusivity_reference_pressure=diffusivity_reference_pressure,
        vapor_pressure=vapor_pressure,
        degrees_of_freedom=degrees_of_freedom,
        emissivity=emissivity,
        scattering_factor=scattering_factor,
        heat_of_pyrolysis=heat_of_pyrolysis,
        swelling_coefficient=swelling_coefficient,
        burn_stoichiometry=burn_stoichiometry,
        combustible_fraction=combustible_fraction,
        burn_hreact=burn_hreact,
        burn_hreact_fraction=burn_hreact_fraction,
        devolatilization_model=devolatilization_model,
        combustion_model=combustion_model,
        averaging_coefficient_t=averaging_coefficient_t,
        averaging_coefficient_y=averaging_coefficient_y,
        vaporization_model=vaporization_model,
        thermolysis_model=thermolysis_model,
        melting_heat=melting_heat,
        tsolidus=tsolidus,
        tliqidus=tliqidus,
        tmelt=tmelt,
        liquidus_slope=liquidus_slope,
        partition_coeff=partition_coeff,
        eutectic_mf=eutectic_mf,
        eutectic_temp=eutectic_temp,
        solut_exp_coeff=solut_exp_coeff,
        solid_diffusion=solid_diffusion,
        uds_diffusivity=uds_diffusivity,
        dpm_surften=dpm_surften,
        electric_conductivity=electric_conductivity,
        dual_electric_conductivity=dual_electric_conductivity,
        lithium_diffusivity=lithium_diffusivity,
        magnetic_permeability=magnetic_permeability,
        charge_density=charge_density,
        charge=charge,
        speed_of_sound=speed_of_sound,
        species_phase=species_phase,
        vp_equilib=vp_equilib,
        critical_temperature=critical_temperature,
        critical_pressure=critical_pressure,
        critical_volume=critical_volume,
        acentric_factor=acentric_factor,
        saturation_pressure=saturation_pressure,
        struct_youngs_modulus=struct_youngs_modulus,
        struct_poisson_ratio=struct_poisson_ratio,
        struct_start_temperature=struct_start_temperature,
        struct_thermal_expansion=struct_thermal_expansion,
        atomic_number=atomic_number,
        struct_damping_alpha=struct_damping_alpha,
        struct_damping_beta=struct_damping_beta,
    )
    return_type = 'object'

class solid(NamedObject[solid_child], CreatableNamedObjectMixinOld[solid_child]):
    """
    'solid' child.
    """
    _version = '222'
    fluent_name = 'solid'
    _python_name = 'solid'
    child_object_type = solid_child
    return_type = 'object'

class mixture_species_child(Group):
    """
    'child_object_type' of mixture_species.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'mixture_species_child'
    child_names = ['species', 'reactions', 'reaction_mechs', 'density', 'specific_heat', 'thermal_conductivity', 'viscosity', 'molecular_weight', 'mass_diffusivity', 'thermal_diffusivity', 'formation_enthalpy', 'formation_entropy', 'characteristic_vibrational_temperature', 'reference_temperature', 'lennard_jones_length', 'lennard_jones_energy', 'thermal_accom_coefficient', 'velocity_accom_coefficient', 'absorption_coefficient', 'scattering_coefficient', 'scattering_phase_function', 'therm_exp_coeff', 'premix_unburnt_density', 'premix_unburnt_temp', 'premix_adiabatic_temp', 'premix_unburnt_cp', 'premix_heat_trans_coeff', 'premix_laminar_speed', 'premix_laminar_thickness', 'premix_critical_strain', 'premix_heat_of_comb', 'premix_unburnt_fuel_mf', 'refractive_index', 'latent_heat', 'thermophoretic_co', 'vaporization_temperature', 'boiling_point', 'volatile_fraction', 'binary_diffusivity', 'diffusivity_reference_pressure', 'vapor_pressure', 'degrees_of_freedom', 'emissivity', 'scattering_factor', 'heat_of_pyrolysis', 'swelling_coefficient', 'burn_stoichiometry', 'combustible_fraction', 'burn_hreact', 'burn_hreact_fraction', 'devolatilization_model', 'combustion_model', 'averaging_coefficient_t', 'averaging_coefficient_y', 'vaporization_model', 'thermolysis_model', 'melting_heat', 'tsolidus', 'tliqidus', 'tmelt', 'liquidus_slope', 'partition_coeff', 'eutectic_mf', 'eutectic_temp', 'solut_exp_coeff', 'solid_diffusion', 'uds_diffusivity', 'dpm_surften', 'electric_conductivity', 'dual_electric_conductivity', 'lithium_diffusivity', 'magnetic_permeability', 'charge_density', 'charge', 'speed_of_sound', 'species_phase', 'vp_equilib', 'critical_temperature', 'critical_pressure', 'critical_volume', 'acentric_factor', 'saturation_pressure', 'struct_youngs_modulus', 'struct_poisson_ratio', 'struct_start_temperature', 'struct_thermal_expansion', 'atomic_number', 'struct_damping_alpha', 'struct_damping_beta']
    _child_classes = dict(
        species=species,
        reactions=reactions,
        reaction_mechs=reaction_mechs,
        density=density,
        specific_heat=specific_heat,
        thermal_conductivity=thermal_conductivity,
        viscosity=viscosity,
        molecular_weight=molecular_weight,
        mass_diffusivity=mass_diffusivity,
        thermal_diffusivity=thermal_diffusivity,
        formation_enthalpy=formation_enthalpy,
        formation_entropy=formation_entropy,
        characteristic_vibrational_temperature=characteristic_vibrational_temperature,
        reference_temperature=reference_temperature,
        lennard_jones_length=lennard_jones_length,
        lennard_jones_energy=lennard_jones_energy,
        thermal_accom_coefficient=thermal_accom_coefficient,
        velocity_accom_coefficient=velocity_accom_coefficient,
        absorption_coefficient=absorption_coefficient,
        scattering_coefficient=scattering_coefficient,
        scattering_phase_function=scattering_phase_function,
        therm_exp_coeff=therm_exp_coeff,
        premix_unburnt_density=premix_unburnt_density,
        premix_unburnt_temp=premix_unburnt_temp,
        premix_adiabatic_temp=premix_adiabatic_temp,
        premix_unburnt_cp=premix_unburnt_cp,
        premix_heat_trans_coeff=premix_heat_trans_coeff,
        premix_laminar_speed=premix_laminar_speed,
        premix_laminar_thickness=premix_laminar_thickness,
        premix_critical_strain=premix_critical_strain,
        premix_heat_of_comb=premix_heat_of_comb,
        premix_unburnt_fuel_mf=premix_unburnt_fuel_mf,
        refractive_index=refractive_index,
        latent_heat=latent_heat,
        thermophoretic_co=thermophoretic_co,
        vaporization_temperature=vaporization_temperature,
        boiling_point=boiling_point,
        volatile_fraction=volatile_fraction,
        binary_diffusivity=binary_diffusivity,
        diffusivity_reference_pressure=diffusivity_reference_pressure,
        vapor_pressure=vapor_pressure,
        degrees_of_freedom=degrees_of_freedom,
        emissivity=emissivity,
        scattering_factor=scattering_factor,
        heat_of_pyrolysis=heat_of_pyrolysis,
        swelling_coefficient=swelling_coefficient,
        burn_stoichiometry=burn_stoichiometry,
        combustible_fraction=combustible_fraction,
        burn_hreact=burn_hreact,
        burn_hreact_fraction=burn_hreact_fraction,
        devolatilization_model=devolatilization_model,
        combustion_model=combustion_model,
        averaging_coefficient_t=averaging_coefficient_t,
        averaging_coefficient_y=averaging_coefficient_y,
        vaporization_model=vaporization_model,
        thermolysis_model=thermolysis_model,
        melting_heat=melting_heat,
        tsolidus=tsolidus,
        tliqidus=tliqidus,
        tmelt=tmelt,
        liquidus_slope=liquidus_slope,
        partition_coeff=partition_coeff,
        eutectic_mf=eutectic_mf,
        eutectic_temp=eutectic_temp,
        solut_exp_coeff=solut_exp_coeff,
        solid_diffusion=solid_diffusion,
        uds_diffusivity=uds_diffusivity,
        dpm_surften=dpm_surften,
        electric_conductivity=electric_conductivity,
        dual_electric_conductivity=dual_electric_conductivity,
        lithium_diffusivity=lithium_diffusivity,
        magnetic_permeability=magnetic_permeability,
        charge_density=charge_density,
        charge=charge,
        speed_of_sound=speed_of_sound,
        species_phase=species_phase,
        vp_equilib=vp_equilib,
        critical_temperature=critical_temperature,
        critical_pressure=critical_pressure,
        critical_volume=critical_volume,
        acentric_factor=acentric_factor,
        saturation_pressure=saturation_pressure,
        struct_youngs_modulus=struct_youngs_modulus,
        struct_poisson_ratio=struct_poisson_ratio,
        struct_start_temperature=struct_start_temperature,
        struct_thermal_expansion=struct_thermal_expansion,
        atomic_number=atomic_number,
        struct_damping_alpha=struct_damping_alpha,
        struct_damping_beta=struct_damping_beta,
    )
    return_type = 'object'

class mixture_species(NamedObject[mixture_species_child], CreatableNamedObjectMixinOld[mixture_species_child]):
    """
    'mixture_species' child.
    """
    _version = '222'
    fluent_name = 'mixture-species'
    _python_name = 'mixture_species'
    child_object_type = mixture_species_child
    return_type = 'object'

class mixture_child(Group):
    """
    'child_object_type' of mixture.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'mixture_child'
    child_names = ['species', 'reactions', 'reaction_mechs', 'density', 'specific_heat', 'thermal_conductivity', 'viscosity', 'molecular_weight', 'mass_diffusivity', 'thermal_diffusivity', 'formation_enthalpy', 'formation_entropy', 'characteristic_vibrational_temperature', 'reference_temperature', 'lennard_jones_length', 'lennard_jones_energy', 'thermal_accom_coefficient', 'velocity_accom_coefficient', 'absorption_coefficient', 'scattering_coefficient', 'scattering_phase_function', 'therm_exp_coeff', 'premix_unburnt_density', 'premix_unburnt_temp', 'premix_adiabatic_temp', 'premix_unburnt_cp', 'premix_heat_trans_coeff', 'premix_laminar_speed', 'premix_laminar_thickness', 'premix_critical_strain', 'premix_heat_of_comb', 'premix_unburnt_fuel_mf', 'refractive_index', 'latent_heat', 'thermophoretic_co', 'vaporization_temperature', 'boiling_point', 'volatile_fraction', 'binary_diffusivity', 'diffusivity_reference_pressure', 'vapor_pressure', 'degrees_of_freedom', 'emissivity', 'scattering_factor', 'heat_of_pyrolysis', 'swelling_coefficient', 'burn_stoichiometry', 'combustible_fraction', 'burn_hreact', 'burn_hreact_fraction', 'devolatilization_model', 'combustion_model', 'averaging_coefficient_t', 'averaging_coefficient_y', 'vaporization_model', 'thermolysis_model', 'melting_heat', 'tsolidus', 'tliqidus', 'tmelt', 'liquidus_slope', 'partition_coeff', 'eutectic_mf', 'eutectic_temp', 'solut_exp_coeff', 'solid_diffusion', 'uds_diffusivity', 'dpm_surften', 'electric_conductivity', 'dual_electric_conductivity', 'lithium_diffusivity', 'magnetic_permeability', 'charge_density', 'charge', 'speed_of_sound', 'species_phase', 'vp_equilib', 'critical_temperature', 'critical_pressure', 'critical_volume', 'acentric_factor', 'saturation_pressure', 'struct_youngs_modulus', 'struct_poisson_ratio', 'struct_start_temperature', 'struct_thermal_expansion', 'atomic_number', 'struct_damping_alpha', 'struct_damping_beta', 'mixture_species']
    _child_classes = dict(
        species=species,
        reactions=reactions,
        reaction_mechs=reaction_mechs,
        density=density,
        specific_heat=specific_heat,
        thermal_conductivity=thermal_conductivity,
        viscosity=viscosity,
        molecular_weight=molecular_weight,
        mass_diffusivity=mass_diffusivity,
        thermal_diffusivity=thermal_diffusivity,
        formation_enthalpy=formation_enthalpy,
        formation_entropy=formation_entropy,
        characteristic_vibrational_temperature=characteristic_vibrational_temperature,
        reference_temperature=reference_temperature,
        lennard_jones_length=lennard_jones_length,
        lennard_jones_energy=lennard_jones_energy,
        thermal_accom_coefficient=thermal_accom_coefficient,
        velocity_accom_coefficient=velocity_accom_coefficient,
        absorption_coefficient=absorption_coefficient,
        scattering_coefficient=scattering_coefficient,
        scattering_phase_function=scattering_phase_function,
        therm_exp_coeff=therm_exp_coeff,
        premix_unburnt_density=premix_unburnt_density,
        premix_unburnt_temp=premix_unburnt_temp,
        premix_adiabatic_temp=premix_adiabatic_temp,
        premix_unburnt_cp=premix_unburnt_cp,
        premix_heat_trans_coeff=premix_heat_trans_coeff,
        premix_laminar_speed=premix_laminar_speed,
        premix_laminar_thickness=premix_laminar_thickness,
        premix_critical_strain=premix_critical_strain,
        premix_heat_of_comb=premix_heat_of_comb,
        premix_unburnt_fuel_mf=premix_unburnt_fuel_mf,
        refractive_index=refractive_index,
        latent_heat=latent_heat,
        thermophoretic_co=thermophoretic_co,
        vaporization_temperature=vaporization_temperature,
        boiling_point=boiling_point,
        volatile_fraction=volatile_fraction,
        binary_diffusivity=binary_diffusivity,
        diffusivity_reference_pressure=diffusivity_reference_pressure,
        vapor_pressure=vapor_pressure,
        degrees_of_freedom=degrees_of_freedom,
        emissivity=emissivity,
        scattering_factor=scattering_factor,
        heat_of_pyrolysis=heat_of_pyrolysis,
        swelling_coefficient=swelling_coefficient,
        burn_stoichiometry=burn_stoichiometry,
        combustible_fraction=combustible_fraction,
        burn_hreact=burn_hreact,
        burn_hreact_fraction=burn_hreact_fraction,
        devolatilization_model=devolatilization_model,
        combustion_model=combustion_model,
        averaging_coefficient_t=averaging_coefficient_t,
        averaging_coefficient_y=averaging_coefficient_y,
        vaporization_model=vaporization_model,
        thermolysis_model=thermolysis_model,
        melting_heat=melting_heat,
        tsolidus=tsolidus,
        tliqidus=tliqidus,
        tmelt=tmelt,
        liquidus_slope=liquidus_slope,
        partition_coeff=partition_coeff,
        eutectic_mf=eutectic_mf,
        eutectic_temp=eutectic_temp,
        solut_exp_coeff=solut_exp_coeff,
        solid_diffusion=solid_diffusion,
        uds_diffusivity=uds_diffusivity,
        dpm_surften=dpm_surften,
        electric_conductivity=electric_conductivity,
        dual_electric_conductivity=dual_electric_conductivity,
        lithium_diffusivity=lithium_diffusivity,
        magnetic_permeability=magnetic_permeability,
        charge_density=charge_density,
        charge=charge,
        speed_of_sound=speed_of_sound,
        species_phase=species_phase,
        vp_equilib=vp_equilib,
        critical_temperature=critical_temperature,
        critical_pressure=critical_pressure,
        critical_volume=critical_volume,
        acentric_factor=acentric_factor,
        saturation_pressure=saturation_pressure,
        struct_youngs_modulus=struct_youngs_modulus,
        struct_poisson_ratio=struct_poisson_ratio,
        struct_start_temperature=struct_start_temperature,
        struct_thermal_expansion=struct_thermal_expansion,
        atomic_number=atomic_number,
        struct_damping_alpha=struct_damping_alpha,
        struct_damping_beta=struct_damping_beta,
        mixture_species=mixture_species,
    )
    return_type = 'object'

class mixture(NamedObject[mixture_child], CreatableNamedObjectMixinOld[mixture_child]):
    """
    'mixture' child.
    """
    _version = '222'
    fluent_name = 'mixture'
    _python_name = 'mixture'
    child_object_type = mixture_child
    return_type = 'object'

class inert_particle_child(Group):
    """
    'child_object_type' of inert_particle.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'inert_particle_child'
    child_names = ['species', 'reactions', 'reaction_mechs', 'density', 'specific_heat', 'thermal_conductivity', 'viscosity', 'molecular_weight', 'mass_diffusivity', 'thermal_diffusivity', 'formation_enthalpy', 'formation_entropy', 'characteristic_vibrational_temperature', 'reference_temperature', 'lennard_jones_length', 'lennard_jones_energy', 'thermal_accom_coefficient', 'velocity_accom_coefficient', 'absorption_coefficient', 'scattering_coefficient', 'scattering_phase_function', 'therm_exp_coeff', 'premix_unburnt_density', 'premix_unburnt_temp', 'premix_adiabatic_temp', 'premix_unburnt_cp', 'premix_heat_trans_coeff', 'premix_laminar_speed', 'premix_laminar_thickness', 'premix_critical_strain', 'premix_heat_of_comb', 'premix_unburnt_fuel_mf', 'refractive_index', 'latent_heat', 'thermophoretic_co', 'vaporization_temperature', 'boiling_point', 'volatile_fraction', 'binary_diffusivity', 'diffusivity_reference_pressure', 'vapor_pressure', 'degrees_of_freedom', 'emissivity', 'scattering_factor', 'heat_of_pyrolysis', 'swelling_coefficient', 'burn_stoichiometry', 'combustible_fraction', 'burn_hreact', 'burn_hreact_fraction', 'devolatilization_model', 'combustion_model', 'averaging_coefficient_t', 'averaging_coefficient_y', 'vaporization_model', 'thermolysis_model', 'melting_heat', 'tsolidus', 'tliqidus', 'tmelt', 'liquidus_slope', 'partition_coeff', 'eutectic_mf', 'eutectic_temp', 'solut_exp_coeff', 'solid_diffusion', 'uds_diffusivity', 'dpm_surften', 'electric_conductivity', 'dual_electric_conductivity', 'lithium_diffusivity', 'magnetic_permeability', 'charge_density', 'charge', 'speed_of_sound', 'species_phase', 'vp_equilib', 'critical_temperature', 'critical_pressure', 'critical_volume', 'acentric_factor', 'saturation_pressure', 'struct_youngs_modulus', 'struct_poisson_ratio', 'struct_start_temperature', 'struct_thermal_expansion', 'atomic_number', 'struct_damping_alpha', 'struct_damping_beta']
    _child_classes = dict(
        species=species,
        reactions=reactions,
        reaction_mechs=reaction_mechs,
        density=density,
        specific_heat=specific_heat,
        thermal_conductivity=thermal_conductivity,
        viscosity=viscosity,
        molecular_weight=molecular_weight,
        mass_diffusivity=mass_diffusivity,
        thermal_diffusivity=thermal_diffusivity,
        formation_enthalpy=formation_enthalpy,
        formation_entropy=formation_entropy,
        characteristic_vibrational_temperature=characteristic_vibrational_temperature,
        reference_temperature=reference_temperature,
        lennard_jones_length=lennard_jones_length,
        lennard_jones_energy=lennard_jones_energy,
        thermal_accom_coefficient=thermal_accom_coefficient,
        velocity_accom_coefficient=velocity_accom_coefficient,
        absorption_coefficient=absorption_coefficient,
        scattering_coefficient=scattering_coefficient,
        scattering_phase_function=scattering_phase_function,
        therm_exp_coeff=therm_exp_coeff,
        premix_unburnt_density=premix_unburnt_density,
        premix_unburnt_temp=premix_unburnt_temp,
        premix_adiabatic_temp=premix_adiabatic_temp,
        premix_unburnt_cp=premix_unburnt_cp,
        premix_heat_trans_coeff=premix_heat_trans_coeff,
        premix_laminar_speed=premix_laminar_speed,
        premix_laminar_thickness=premix_laminar_thickness,
        premix_critical_strain=premix_critical_strain,
        premix_heat_of_comb=premix_heat_of_comb,
        premix_unburnt_fuel_mf=premix_unburnt_fuel_mf,
        refractive_index=refractive_index,
        latent_heat=latent_heat,
        thermophoretic_co=thermophoretic_co,
        vaporization_temperature=vaporization_temperature,
        boiling_point=boiling_point,
        volatile_fraction=volatile_fraction,
        binary_diffusivity=binary_diffusivity,
        diffusivity_reference_pressure=diffusivity_reference_pressure,
        vapor_pressure=vapor_pressure,
        degrees_of_freedom=degrees_of_freedom,
        emissivity=emissivity,
        scattering_factor=scattering_factor,
        heat_of_pyrolysis=heat_of_pyrolysis,
        swelling_coefficient=swelling_coefficient,
        burn_stoichiometry=burn_stoichiometry,
        combustible_fraction=combustible_fraction,
        burn_hreact=burn_hreact,
        burn_hreact_fraction=burn_hreact_fraction,
        devolatilization_model=devolatilization_model,
        combustion_model=combustion_model,
        averaging_coefficient_t=averaging_coefficient_t,
        averaging_coefficient_y=averaging_coefficient_y,
        vaporization_model=vaporization_model,
        thermolysis_model=thermolysis_model,
        melting_heat=melting_heat,
        tsolidus=tsolidus,
        tliqidus=tliqidus,
        tmelt=tmelt,
        liquidus_slope=liquidus_slope,
        partition_coeff=partition_coeff,
        eutectic_mf=eutectic_mf,
        eutectic_temp=eutectic_temp,
        solut_exp_coeff=solut_exp_coeff,
        solid_diffusion=solid_diffusion,
        uds_diffusivity=uds_diffusivity,
        dpm_surften=dpm_surften,
        electric_conductivity=electric_conductivity,
        dual_electric_conductivity=dual_electric_conductivity,
        lithium_diffusivity=lithium_diffusivity,
        magnetic_permeability=magnetic_permeability,
        charge_density=charge_density,
        charge=charge,
        speed_of_sound=speed_of_sound,
        species_phase=species_phase,
        vp_equilib=vp_equilib,
        critical_temperature=critical_temperature,
        critical_pressure=critical_pressure,
        critical_volume=critical_volume,
        acentric_factor=acentric_factor,
        saturation_pressure=saturation_pressure,
        struct_youngs_modulus=struct_youngs_modulus,
        struct_poisson_ratio=struct_poisson_ratio,
        struct_start_temperature=struct_start_temperature,
        struct_thermal_expansion=struct_thermal_expansion,
        atomic_number=atomic_number,
        struct_damping_alpha=struct_damping_alpha,
        struct_damping_beta=struct_damping_beta,
    )
    return_type = 'object'

class inert_particle(NamedObject[inert_particle_child], CreatableNamedObjectMixinOld[inert_particle_child]):
    """
    'inert_particle' child.
    """
    _version = '222'
    fluent_name = 'inert-particle'
    _python_name = 'inert_particle'
    child_object_type = inert_particle_child
    return_type = 'object'

class droplet_particle_child(Group):
    """
    'child_object_type' of droplet_particle.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'droplet_particle_child'
    child_names = ['species', 'reactions', 'reaction_mechs', 'density', 'specific_heat', 'thermal_conductivity', 'viscosity', 'molecular_weight', 'mass_diffusivity', 'thermal_diffusivity', 'formation_enthalpy', 'formation_entropy', 'characteristic_vibrational_temperature', 'reference_temperature', 'lennard_jones_length', 'lennard_jones_energy', 'thermal_accom_coefficient', 'velocity_accom_coefficient', 'absorption_coefficient', 'scattering_coefficient', 'scattering_phase_function', 'therm_exp_coeff', 'premix_unburnt_density', 'premix_unburnt_temp', 'premix_adiabatic_temp', 'premix_unburnt_cp', 'premix_heat_trans_coeff', 'premix_laminar_speed', 'premix_laminar_thickness', 'premix_critical_strain', 'premix_heat_of_comb', 'premix_unburnt_fuel_mf', 'refractive_index', 'latent_heat', 'thermophoretic_co', 'vaporization_temperature', 'boiling_point', 'volatile_fraction', 'binary_diffusivity', 'diffusivity_reference_pressure', 'vapor_pressure', 'degrees_of_freedom', 'emissivity', 'scattering_factor', 'heat_of_pyrolysis', 'swelling_coefficient', 'burn_stoichiometry', 'combustible_fraction', 'burn_hreact', 'burn_hreact_fraction', 'devolatilization_model', 'combustion_model', 'averaging_coefficient_t', 'averaging_coefficient_y', 'vaporization_model', 'thermolysis_model', 'melting_heat', 'tsolidus', 'tliqidus', 'tmelt', 'liquidus_slope', 'partition_coeff', 'eutectic_mf', 'eutectic_temp', 'solut_exp_coeff', 'solid_diffusion', 'uds_diffusivity', 'dpm_surften', 'electric_conductivity', 'dual_electric_conductivity', 'lithium_diffusivity', 'magnetic_permeability', 'charge_density', 'charge', 'speed_of_sound', 'species_phase', 'vp_equilib', 'critical_temperature', 'critical_pressure', 'critical_volume', 'acentric_factor', 'saturation_pressure', 'struct_youngs_modulus', 'struct_poisson_ratio', 'struct_start_temperature', 'struct_thermal_expansion', 'atomic_number', 'struct_damping_alpha', 'struct_damping_beta']
    _child_classes = dict(
        species=species,
        reactions=reactions,
        reaction_mechs=reaction_mechs,
        density=density,
        specific_heat=specific_heat,
        thermal_conductivity=thermal_conductivity,
        viscosity=viscosity,
        molecular_weight=molecular_weight,
        mass_diffusivity=mass_diffusivity,
        thermal_diffusivity=thermal_diffusivity,
        formation_enthalpy=formation_enthalpy,
        formation_entropy=formation_entropy,
        characteristic_vibrational_temperature=characteristic_vibrational_temperature,
        reference_temperature=reference_temperature,
        lennard_jones_length=lennard_jones_length,
        lennard_jones_energy=lennard_jones_energy,
        thermal_accom_coefficient=thermal_accom_coefficient,
        velocity_accom_coefficient=velocity_accom_coefficient,
        absorption_coefficient=absorption_coefficient,
        scattering_coefficient=scattering_coefficient,
        scattering_phase_function=scattering_phase_function,
        therm_exp_coeff=therm_exp_coeff,
        premix_unburnt_density=premix_unburnt_density,
        premix_unburnt_temp=premix_unburnt_temp,
        premix_adiabatic_temp=premix_adiabatic_temp,
        premix_unburnt_cp=premix_unburnt_cp,
        premix_heat_trans_coeff=premix_heat_trans_coeff,
        premix_laminar_speed=premix_laminar_speed,
        premix_laminar_thickness=premix_laminar_thickness,
        premix_critical_strain=premix_critical_strain,
        premix_heat_of_comb=premix_heat_of_comb,
        premix_unburnt_fuel_mf=premix_unburnt_fuel_mf,
        refractive_index=refractive_index,
        latent_heat=latent_heat,
        thermophoretic_co=thermophoretic_co,
        vaporization_temperature=vaporization_temperature,
        boiling_point=boiling_point,
        volatile_fraction=volatile_fraction,
        binary_diffusivity=binary_diffusivity,
        diffusivity_reference_pressure=diffusivity_reference_pressure,
        vapor_pressure=vapor_pressure,
        degrees_of_freedom=degrees_of_freedom,
        emissivity=emissivity,
        scattering_factor=scattering_factor,
        heat_of_pyrolysis=heat_of_pyrolysis,
        swelling_coefficient=swelling_coefficient,
        burn_stoichiometry=burn_stoichiometry,
        combustible_fraction=combustible_fraction,
        burn_hreact=burn_hreact,
        burn_hreact_fraction=burn_hreact_fraction,
        devolatilization_model=devolatilization_model,
        combustion_model=combustion_model,
        averaging_coefficient_t=averaging_coefficient_t,
        averaging_coefficient_y=averaging_coefficient_y,
        vaporization_model=vaporization_model,
        thermolysis_model=thermolysis_model,
        melting_heat=melting_heat,
        tsolidus=tsolidus,
        tliqidus=tliqidus,
        tmelt=tmelt,
        liquidus_slope=liquidus_slope,
        partition_coeff=partition_coeff,
        eutectic_mf=eutectic_mf,
        eutectic_temp=eutectic_temp,
        solut_exp_coeff=solut_exp_coeff,
        solid_diffusion=solid_diffusion,
        uds_diffusivity=uds_diffusivity,
        dpm_surften=dpm_surften,
        electric_conductivity=electric_conductivity,
        dual_electric_conductivity=dual_electric_conductivity,
        lithium_diffusivity=lithium_diffusivity,
        magnetic_permeability=magnetic_permeability,
        charge_density=charge_density,
        charge=charge,
        speed_of_sound=speed_of_sound,
        species_phase=species_phase,
        vp_equilib=vp_equilib,
        critical_temperature=critical_temperature,
        critical_pressure=critical_pressure,
        critical_volume=critical_volume,
        acentric_factor=acentric_factor,
        saturation_pressure=saturation_pressure,
        struct_youngs_modulus=struct_youngs_modulus,
        struct_poisson_ratio=struct_poisson_ratio,
        struct_start_temperature=struct_start_temperature,
        struct_thermal_expansion=struct_thermal_expansion,
        atomic_number=atomic_number,
        struct_damping_alpha=struct_damping_alpha,
        struct_damping_beta=struct_damping_beta,
    )
    return_type = 'object'

class droplet_particle(NamedObject[droplet_particle_child], CreatableNamedObjectMixinOld[droplet_particle_child]):
    """
    'droplet_particle' child.
    """
    _version = '222'
    fluent_name = 'droplet-particle'
    _python_name = 'droplet_particle'
    child_object_type = droplet_particle_child
    return_type = 'object'

class combusting_particle_child(Group):
    """
    'child_object_type' of combusting_particle.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'combusting_particle_child'
    child_names = ['species', 'reactions', 'reaction_mechs', 'density', 'specific_heat', 'thermal_conductivity', 'viscosity', 'molecular_weight', 'mass_diffusivity', 'thermal_diffusivity', 'formation_enthalpy', 'formation_entropy', 'characteristic_vibrational_temperature', 'reference_temperature', 'lennard_jones_length', 'lennard_jones_energy', 'thermal_accom_coefficient', 'velocity_accom_coefficient', 'absorption_coefficient', 'scattering_coefficient', 'scattering_phase_function', 'therm_exp_coeff', 'premix_unburnt_density', 'premix_unburnt_temp', 'premix_adiabatic_temp', 'premix_unburnt_cp', 'premix_heat_trans_coeff', 'premix_laminar_speed', 'premix_laminar_thickness', 'premix_critical_strain', 'premix_heat_of_comb', 'premix_unburnt_fuel_mf', 'refractive_index', 'latent_heat', 'thermophoretic_co', 'vaporization_temperature', 'boiling_point', 'volatile_fraction', 'binary_diffusivity', 'diffusivity_reference_pressure', 'vapor_pressure', 'degrees_of_freedom', 'emissivity', 'scattering_factor', 'heat_of_pyrolysis', 'swelling_coefficient', 'burn_stoichiometry', 'combustible_fraction', 'burn_hreact', 'burn_hreact_fraction', 'devolatilization_model', 'combustion_model', 'averaging_coefficient_t', 'averaging_coefficient_y', 'vaporization_model', 'thermolysis_model', 'melting_heat', 'tsolidus', 'tliqidus', 'tmelt', 'liquidus_slope', 'partition_coeff', 'eutectic_mf', 'eutectic_temp', 'solut_exp_coeff', 'solid_diffusion', 'uds_diffusivity', 'dpm_surften', 'electric_conductivity', 'dual_electric_conductivity', 'lithium_diffusivity', 'magnetic_permeability', 'charge_density', 'charge', 'speed_of_sound', 'species_phase', 'vp_equilib', 'critical_temperature', 'critical_pressure', 'critical_volume', 'acentric_factor', 'saturation_pressure', 'struct_youngs_modulus', 'struct_poisson_ratio', 'struct_start_temperature', 'struct_thermal_expansion', 'atomic_number', 'struct_damping_alpha', 'struct_damping_beta']
    _child_classes = dict(
        species=species,
        reactions=reactions,
        reaction_mechs=reaction_mechs,
        density=density,
        specific_heat=specific_heat,
        thermal_conductivity=thermal_conductivity,
        viscosity=viscosity,
        molecular_weight=molecular_weight,
        mass_diffusivity=mass_diffusivity,
        thermal_diffusivity=thermal_diffusivity,
        formation_enthalpy=formation_enthalpy,
        formation_entropy=formation_entropy,
        characteristic_vibrational_temperature=characteristic_vibrational_temperature,
        reference_temperature=reference_temperature,
        lennard_jones_length=lennard_jones_length,
        lennard_jones_energy=lennard_jones_energy,
        thermal_accom_coefficient=thermal_accom_coefficient,
        velocity_accom_coefficient=velocity_accom_coefficient,
        absorption_coefficient=absorption_coefficient,
        scattering_coefficient=scattering_coefficient,
        scattering_phase_function=scattering_phase_function,
        therm_exp_coeff=therm_exp_coeff,
        premix_unburnt_density=premix_unburnt_density,
        premix_unburnt_temp=premix_unburnt_temp,
        premix_adiabatic_temp=premix_adiabatic_temp,
        premix_unburnt_cp=premix_unburnt_cp,
        premix_heat_trans_coeff=premix_heat_trans_coeff,
        premix_laminar_speed=premix_laminar_speed,
        premix_laminar_thickness=premix_laminar_thickness,
        premix_critical_strain=premix_critical_strain,
        premix_heat_of_comb=premix_heat_of_comb,
        premix_unburnt_fuel_mf=premix_unburnt_fuel_mf,
        refractive_index=refractive_index,
        latent_heat=latent_heat,
        thermophoretic_co=thermophoretic_co,
        vaporization_temperature=vaporization_temperature,
        boiling_point=boiling_point,
        volatile_fraction=volatile_fraction,
        binary_diffusivity=binary_diffusivity,
        diffusivity_reference_pressure=diffusivity_reference_pressure,
        vapor_pressure=vapor_pressure,
        degrees_of_freedom=degrees_of_freedom,
        emissivity=emissivity,
        scattering_factor=scattering_factor,
        heat_of_pyrolysis=heat_of_pyrolysis,
        swelling_coefficient=swelling_coefficient,
        burn_stoichiometry=burn_stoichiometry,
        combustible_fraction=combustible_fraction,
        burn_hreact=burn_hreact,
        burn_hreact_fraction=burn_hreact_fraction,
        devolatilization_model=devolatilization_model,
        combustion_model=combustion_model,
        averaging_coefficient_t=averaging_coefficient_t,
        averaging_coefficient_y=averaging_coefficient_y,
        vaporization_model=vaporization_model,
        thermolysis_model=thermolysis_model,
        melting_heat=melting_heat,
        tsolidus=tsolidus,
        tliqidus=tliqidus,
        tmelt=tmelt,
        liquidus_slope=liquidus_slope,
        partition_coeff=partition_coeff,
        eutectic_mf=eutectic_mf,
        eutectic_temp=eutectic_temp,
        solut_exp_coeff=solut_exp_coeff,
        solid_diffusion=solid_diffusion,
        uds_diffusivity=uds_diffusivity,
        dpm_surften=dpm_surften,
        electric_conductivity=electric_conductivity,
        dual_electric_conductivity=dual_electric_conductivity,
        lithium_diffusivity=lithium_diffusivity,
        magnetic_permeability=magnetic_permeability,
        charge_density=charge_density,
        charge=charge,
        speed_of_sound=speed_of_sound,
        species_phase=species_phase,
        vp_equilib=vp_equilib,
        critical_temperature=critical_temperature,
        critical_pressure=critical_pressure,
        critical_volume=critical_volume,
        acentric_factor=acentric_factor,
        saturation_pressure=saturation_pressure,
        struct_youngs_modulus=struct_youngs_modulus,
        struct_poisson_ratio=struct_poisson_ratio,
        struct_start_temperature=struct_start_temperature,
        struct_thermal_expansion=struct_thermal_expansion,
        atomic_number=atomic_number,
        struct_damping_alpha=struct_damping_alpha,
        struct_damping_beta=struct_damping_beta,
    )
    return_type = 'object'

class combusting_particle(NamedObject[combusting_particle_child], CreatableNamedObjectMixinOld[combusting_particle_child]):
    """
    'combusting_particle' child.
    """
    _version = '222'
    fluent_name = 'combusting-particle'
    _python_name = 'combusting_particle'
    child_object_type = combusting_particle_child
    return_type = 'object'

class particle_mixture_child(Group):
    """
    'child_object_type' of particle_mixture.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'particle_mixture_child'
    child_names = ['species', 'reactions', 'reaction_mechs', 'density', 'specific_heat', 'thermal_conductivity', 'viscosity', 'molecular_weight', 'mass_diffusivity', 'thermal_diffusivity', 'formation_enthalpy', 'formation_entropy', 'characteristic_vibrational_temperature', 'reference_temperature', 'lennard_jones_length', 'lennard_jones_energy', 'thermal_accom_coefficient', 'velocity_accom_coefficient', 'absorption_coefficient', 'scattering_coefficient', 'scattering_phase_function', 'therm_exp_coeff', 'premix_unburnt_density', 'premix_unburnt_temp', 'premix_adiabatic_temp', 'premix_unburnt_cp', 'premix_heat_trans_coeff', 'premix_laminar_speed', 'premix_laminar_thickness', 'premix_critical_strain', 'premix_heat_of_comb', 'premix_unburnt_fuel_mf', 'refractive_index', 'latent_heat', 'thermophoretic_co', 'vaporization_temperature', 'boiling_point', 'volatile_fraction', 'binary_diffusivity', 'diffusivity_reference_pressure', 'vapor_pressure', 'degrees_of_freedom', 'emissivity', 'scattering_factor', 'heat_of_pyrolysis', 'swelling_coefficient', 'burn_stoichiometry', 'combustible_fraction', 'burn_hreact', 'burn_hreact_fraction', 'devolatilization_model', 'combustion_model', 'averaging_coefficient_t', 'averaging_coefficient_y', 'vaporization_model', 'thermolysis_model', 'melting_heat', 'tsolidus', 'tliqidus', 'tmelt', 'liquidus_slope', 'partition_coeff', 'eutectic_mf', 'eutectic_temp', 'solut_exp_coeff', 'solid_diffusion', 'uds_diffusivity', 'dpm_surften', 'electric_conductivity', 'dual_electric_conductivity', 'lithium_diffusivity', 'magnetic_permeability', 'charge_density', 'charge', 'speed_of_sound', 'species_phase', 'vp_equilib', 'critical_temperature', 'critical_pressure', 'critical_volume', 'acentric_factor', 'saturation_pressure', 'struct_youngs_modulus', 'struct_poisson_ratio', 'struct_start_temperature', 'struct_thermal_expansion', 'atomic_number', 'struct_damping_alpha', 'struct_damping_beta', 'mixture_species']
    _child_classes = dict(
        species=species,
        reactions=reactions,
        reaction_mechs=reaction_mechs,
        density=density,
        specific_heat=specific_heat,
        thermal_conductivity=thermal_conductivity,
        viscosity=viscosity,
        molecular_weight=molecular_weight,
        mass_diffusivity=mass_diffusivity,
        thermal_diffusivity=thermal_diffusivity,
        formation_enthalpy=formation_enthalpy,
        formation_entropy=formation_entropy,
        characteristic_vibrational_temperature=characteristic_vibrational_temperature,
        reference_temperature=reference_temperature,
        lennard_jones_length=lennard_jones_length,
        lennard_jones_energy=lennard_jones_energy,
        thermal_accom_coefficient=thermal_accom_coefficient,
        velocity_accom_coefficient=velocity_accom_coefficient,
        absorption_coefficient=absorption_coefficient,
        scattering_coefficient=scattering_coefficient,
        scattering_phase_function=scattering_phase_function,
        therm_exp_coeff=therm_exp_coeff,
        premix_unburnt_density=premix_unburnt_density,
        premix_unburnt_temp=premix_unburnt_temp,
        premix_adiabatic_temp=premix_adiabatic_temp,
        premix_unburnt_cp=premix_unburnt_cp,
        premix_heat_trans_coeff=premix_heat_trans_coeff,
        premix_laminar_speed=premix_laminar_speed,
        premix_laminar_thickness=premix_laminar_thickness,
        premix_critical_strain=premix_critical_strain,
        premix_heat_of_comb=premix_heat_of_comb,
        premix_unburnt_fuel_mf=premix_unburnt_fuel_mf,
        refractive_index=refractive_index,
        latent_heat=latent_heat,
        thermophoretic_co=thermophoretic_co,
        vaporization_temperature=vaporization_temperature,
        boiling_point=boiling_point,
        volatile_fraction=volatile_fraction,
        binary_diffusivity=binary_diffusivity,
        diffusivity_reference_pressure=diffusivity_reference_pressure,
        vapor_pressure=vapor_pressure,
        degrees_of_freedom=degrees_of_freedom,
        emissivity=emissivity,
        scattering_factor=scattering_factor,
        heat_of_pyrolysis=heat_of_pyrolysis,
        swelling_coefficient=swelling_coefficient,
        burn_stoichiometry=burn_stoichiometry,
        combustible_fraction=combustible_fraction,
        burn_hreact=burn_hreact,
        burn_hreact_fraction=burn_hreact_fraction,
        devolatilization_model=devolatilization_model,
        combustion_model=combustion_model,
        averaging_coefficient_t=averaging_coefficient_t,
        averaging_coefficient_y=averaging_coefficient_y,
        vaporization_model=vaporization_model,
        thermolysis_model=thermolysis_model,
        melting_heat=melting_heat,
        tsolidus=tsolidus,
        tliqidus=tliqidus,
        tmelt=tmelt,
        liquidus_slope=liquidus_slope,
        partition_coeff=partition_coeff,
        eutectic_mf=eutectic_mf,
        eutectic_temp=eutectic_temp,
        solut_exp_coeff=solut_exp_coeff,
        solid_diffusion=solid_diffusion,
        uds_diffusivity=uds_diffusivity,
        dpm_surften=dpm_surften,
        electric_conductivity=electric_conductivity,
        dual_electric_conductivity=dual_electric_conductivity,
        lithium_diffusivity=lithium_diffusivity,
        magnetic_permeability=magnetic_permeability,
        charge_density=charge_density,
        charge=charge,
        speed_of_sound=speed_of_sound,
        species_phase=species_phase,
        vp_equilib=vp_equilib,
        critical_temperature=critical_temperature,
        critical_pressure=critical_pressure,
        critical_volume=critical_volume,
        acentric_factor=acentric_factor,
        saturation_pressure=saturation_pressure,
        struct_youngs_modulus=struct_youngs_modulus,
        struct_poisson_ratio=struct_poisson_ratio,
        struct_start_temperature=struct_start_temperature,
        struct_thermal_expansion=struct_thermal_expansion,
        atomic_number=atomic_number,
        struct_damping_alpha=struct_damping_alpha,
        struct_damping_beta=struct_damping_beta,
        mixture_species=mixture_species,
    )
    return_type = 'object'

class particle_mixture(NamedObject[particle_mixture_child], CreatableNamedObjectMixinOld[particle_mixture_child]):
    """
    'particle_mixture' child.
    """
    _version = '222'
    fluent_name = 'particle-mixture'
    _python_name = 'particle_mixture'
    child_object_type = particle_mixture_child
    return_type = 'object'

class list_materials(Command):
    """
    'list_materials' command.
    """
    _version = '222'
    fluent_name = 'list-materials'
    _python_name = 'list_materials'
    return_type = 'object'

class type_1(String, AllowedValuesMixin):
    """
    'type' child.
    """
    _version = '222'
    fluent_name = 'type'
    _python_name = 'type'
    return_type = 'object'

class name(String, AllowedValuesMixin):
    """
    'name' child.
    """
    _version = '222'
    fluent_name = 'name'
    _python_name = 'name'
    return_type = 'object'

class copy_database_material_by_name(Command):
    """
    'copy_database_material_by_name' command.
    """
    _version = '222'
    fluent_name = 'copy-database-material-by-name'
    _python_name = 'copy_database_material_by_name'
    argument_names = ['type', 'name']
    _child_classes = dict(
        type=type_1,
        name=name,
    )
    return_type = 'object'

class formula(String, AllowedValuesMixin):
    """
    'formula' child.
    """
    _version = '222'
    fluent_name = 'formula'
    _python_name = 'formula'
    return_type = 'object'

class copy_database_material_by_formula(Command):
    """
    'copy_database_material_by_formula' command.
    """
    _version = '222'
    fluent_name = 'copy-database-material-by-formula'
    _python_name = 'copy_database_material_by_formula'
    argument_names = ['type', 'formula']
    _child_classes = dict(
        type=type_1,
        formula=formula,
    )
    return_type = 'object'

class materials(Group):
    """
    'materials' child.
    """
    _version = '222'
    fluent_name = 'materials'
    _python_name = 'materials'
    child_names = ['fluid', 'solid', 'mixture', 'inert_particle', 'droplet_particle', 'combusting_particle', 'particle_mixture']
    command_names = ['list_materials', 'copy_database_material_by_name', 'copy_database_material_by_formula']
    _child_classes = dict(
        fluid=fluid,
        solid=solid,
        mixture=mixture,
        inert_particle=inert_particle,
        droplet_particle=droplet_particle,
        combusting_particle=combusting_particle,
        particle_mixture=particle_mixture,
        list_materials=list_materials,
        copy_database_material_by_name=copy_database_material_by_name,
        copy_database_material_by_formula=copy_database_material_by_formula,
    )
    return_type = 'object'

class zone_list(StringList, AllowedValuesMixin):
    """
    'zone_list' child.
    """
    _version = '222'
    fluent_name = 'zone-list'
    _python_name = 'zone_list'
    return_type = 'object'

class new_type(String, AllowedValuesMixin):
    """
    'new_type' child.
    """
    _version = '222'
    fluent_name = 'new-type'
    _python_name = 'new_type'
    return_type = 'object'

class change_type(Command):
    """
    'change_type' command.
    """
    _version = '222'
    fluent_name = 'change-type'
    _python_name = 'change_type'
    argument_names = ['zone_list', 'new_type']
    _child_classes = dict(
        zone_list=zone_list,
        new_type=new_type,
    )
    return_type = 'object'

class material(String, AllowedValuesMixin):
    """
    'material' child.
    """
    _version = '222'
    fluent_name = 'material'
    _python_name = 'material'
    return_type = 'object'

class sources(Boolean, AllowedValuesMixin):
    """
    'sources' child.
    """
    _version = '222'
    fluent_name = 'sources?'
    _python_name = 'sources'
    return_type = 'object'

class profile_name(String, AllowedValuesMixin):
    """
    'profile_name' child.
    """
    _version = '222'
    fluent_name = 'profile-name'
    _python_name = 'profile_name'
    return_type = 'object'

class field_name(String, AllowedValuesMixin):
    """
    'field_name' child.
    """
    _version = '222'
    fluent_name = 'field-name'
    _python_name = 'field_name'
    return_type = 'object'

class udf(String, AllowedValuesMixin):
    """
    'udf' child.
    """
    _version = '222'
    fluent_name = 'udf'
    _python_name = 'udf'
    return_type = 'object'

class source_terms_child_child(Group):
    """
    'child_object_type' of child_object_type.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'source_terms_child_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class source_terms_child(ListObject[source_terms_child_child]):
    """
    'child_object_type' of source_terms.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'source_terms_child'
    child_object_type = source_terms_child_child
    return_type = 'object'

class source_terms(NamedObject[source_terms_child], CreatableNamedObjectMixinOld[source_terms_child]):
    """
    'source_terms' child.
    """
    _version = '222'
    fluent_name = 'source-terms'
    _python_name = 'source_terms'
    child_object_type = source_terms_child
    return_type = 'object'

class fixed(Boolean, AllowedValuesMixin):
    """
    'fixed' child.
    """
    _version = '222'
    fluent_name = 'fixed?'
    _python_name = 'fixed'
    return_type = 'object'

class cylindrical_fixed_var(Boolean, AllowedValuesMixin):
    """
    'cylindrical_fixed_var' child.
    """
    _version = '222'
    fluent_name = 'cylindrical-fixed-var?'
    _python_name = 'cylindrical_fixed_var'
    return_type = 'object'

class fixes_child(Group):
    """
    'child_object_type' of fixes.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'fixes_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class fixes(NamedObject[fixes_child], CreatableNamedObjectMixinOld[fixes_child]):
    """
    'fixes' child.
    """
    _version = '222'
    fluent_name = 'fixes'
    _python_name = 'fixes'
    child_object_type = fixes_child
    return_type = 'object'

class motion_spec(String, AllowedValuesMixin):
    """
    'motion_spec' child.
    """
    _version = '222'
    fluent_name = 'motion-spec'
    _python_name = 'motion_spec'
    return_type = 'object'

class relative_to_thread(String, AllowedValuesMixin):
    """
    'relative_to_thread' child.
    """
    _version = '222'
    fluent_name = 'relative-to-thread'
    _python_name = 'relative_to_thread'
    return_type = 'object'

class omega(Group):
    """
    'omega' child.
    """
    _version = '222'
    fluent_name = 'omega'
    _python_name = 'omega'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class axis_origin_component_child(Group):
    """
    'child_object_type' of axis_origin_component.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'axis_origin_component_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class axis_origin_component(ListObject[axis_origin_component_child]):
    """
    'axis_origin_component' child.
    """
    _version = '222'
    fluent_name = 'axis-origin-component'
    _python_name = 'axis_origin_component'
    child_object_type = axis_origin_component_child
    return_type = 'object'

class axis_direction_component_child(Group):
    """
    'child_object_type' of axis_direction_component.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'axis_direction_component_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class axis_direction_component(ListObject[axis_direction_component_child]):
    """
    'axis_direction_component' child.
    """
    _version = '222'
    fluent_name = 'axis-direction-component'
    _python_name = 'axis_direction_component'
    child_object_type = axis_direction_component_child
    return_type = 'object'

class udf_zmotion_name(String, AllowedValuesMixin):
    """
    'udf_zmotion_name' child.
    """
    _version = '222'
    fluent_name = 'udf-zmotion-name'
    _python_name = 'udf_zmotion_name'
    return_type = 'object'

class mrf_motion(Boolean, AllowedValuesMixin):
    """
    'mrf_motion' child.
    """
    _version = '222'
    fluent_name = 'mrf-motion?'
    _python_name = 'mrf_motion'
    return_type = 'object'

class mrf_relative_to_thread(String, AllowedValuesMixin):
    """
    'mrf_relative_to_thread' child.
    """
    _version = '222'
    fluent_name = 'mrf-relative-to-thread'
    _python_name = 'mrf_relative_to_thread'
    return_type = 'object'

class mrf_omega(Group):
    """
    'mrf_omega' child.
    """
    _version = '222'
    fluent_name = 'mrf-omega'
    _python_name = 'mrf_omega'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class reference_frame_velocity_components_child(Group):
    """
    'child_object_type' of reference_frame_velocity_components.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'reference_frame_velocity_components_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class reference_frame_velocity_components(ListObject[reference_frame_velocity_components_child]):
    """
    'reference_frame_velocity_components' child.
    """
    _version = '222'
    fluent_name = 'reference-frame-velocity-components'
    _python_name = 'reference_frame_velocity_components'
    child_object_type = reference_frame_velocity_components_child
    return_type = 'object'

class reference_frame_axis_origin_components_child(Group):
    """
    'child_object_type' of reference_frame_axis_origin_components.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'reference_frame_axis_origin_components_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class reference_frame_axis_origin_components(ListObject[reference_frame_axis_origin_components_child]):
    """
    'reference_frame_axis_origin_components' child.
    """
    _version = '222'
    fluent_name = 'reference-frame-axis-origin-components'
    _python_name = 'reference_frame_axis_origin_components'
    child_object_type = reference_frame_axis_origin_components_child
    return_type = 'object'

class reference_frame_axis_direction_components_child(Group):
    """
    'child_object_type' of reference_frame_axis_direction_components.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'reference_frame_axis_direction_components_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class reference_frame_axis_direction_components(ListObject[reference_frame_axis_direction_components_child]):
    """
    'reference_frame_axis_direction_components' child.
    """
    _version = '222'
    fluent_name = 'reference-frame-axis-direction-components'
    _python_name = 'reference_frame_axis_direction_components'
    child_object_type = reference_frame_axis_direction_components_child
    return_type = 'object'

class mrf_udf_zmotion_name(String, AllowedValuesMixin):
    """
    'mrf_udf_zmotion_name' child.
    """
    _version = '222'
    fluent_name = 'mrf-udf-zmotion-name'
    _python_name = 'mrf_udf_zmotion_name'
    return_type = 'object'

class mgrid_enable_transient(Boolean, AllowedValuesMixin):
    """
    'mgrid_enable_transient' child.
    """
    _version = '222'
    fluent_name = 'mgrid-enable-transient?'
    _python_name = 'mgrid_enable_transient'
    return_type = 'object'

class mgrid_motion(Boolean, AllowedValuesMixin):
    """
    'mgrid_motion' child.
    """
    _version = '222'
    fluent_name = 'mgrid-motion?'
    _python_name = 'mgrid_motion'
    return_type = 'object'

class mgrid_relative_to_thread(String, AllowedValuesMixin):
    """
    'mgrid_relative_to_thread' child.
    """
    _version = '222'
    fluent_name = 'mgrid-relative-to-thread'
    _python_name = 'mgrid_relative_to_thread'
    return_type = 'object'

class mgrid_omega(Group):
    """
    'mgrid_omega' child.
    """
    _version = '222'
    fluent_name = 'mgrid-omega'
    _python_name = 'mgrid_omega'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class moving_mesh_velocity_components_child(Group):
    """
    'child_object_type' of moving_mesh_velocity_components.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'moving_mesh_velocity_components_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class moving_mesh_velocity_components(ListObject[moving_mesh_velocity_components_child]):
    """
    'moving_mesh_velocity_components' child.
    """
    _version = '222'
    fluent_name = 'moving-mesh-velocity-components'
    _python_name = 'moving_mesh_velocity_components'
    child_object_type = moving_mesh_velocity_components_child
    return_type = 'object'

class moving_mesh_axis_origin_components_child(Group):
    """
    'child_object_type' of moving_mesh_axis_origin_components.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'moving_mesh_axis_origin_components_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class moving_mesh_axis_origin_components(ListObject[moving_mesh_axis_origin_components_child]):
    """
    'moving_mesh_axis_origin_components' child.
    """
    _version = '222'
    fluent_name = 'moving-mesh-axis-origin-components'
    _python_name = 'moving_mesh_axis_origin_components'
    child_object_type = moving_mesh_axis_origin_components_child
    return_type = 'object'

class mgrid_udf_zmotion_name(String, AllowedValuesMixin):
    """
    'mgrid_udf_zmotion_name' child.
    """
    _version = '222'
    fluent_name = 'mgrid-udf-zmotion-name'
    _python_name = 'mgrid_udf_zmotion_name'
    return_type = 'object'

class solid_motion(Boolean, AllowedValuesMixin):
    """
    'solid_motion' child.
    """
    _version = '222'
    fluent_name = 'solid-motion?'
    _python_name = 'solid_motion'
    return_type = 'object'

class solid_relative_to_thread(String, AllowedValuesMixin):
    """
    'solid_relative_to_thread' child.
    """
    _version = '222'
    fluent_name = 'solid-relative-to-thread'
    _python_name = 'solid_relative_to_thread'
    return_type = 'object'

class solid_omega(Group):
    """
    'solid_omega' child.
    """
    _version = '222'
    fluent_name = 'solid-omega'
    _python_name = 'solid_omega'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class solid_motion_velocity_components_child(Group):
    """
    'child_object_type' of solid_motion_velocity_components.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'solid_motion_velocity_components_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class solid_motion_velocity_components(ListObject[solid_motion_velocity_components_child]):
    """
    'solid_motion_velocity_components' child.
    """
    _version = '222'
    fluent_name = 'solid-motion-velocity-components'
    _python_name = 'solid_motion_velocity_components'
    child_object_type = solid_motion_velocity_components_child
    return_type = 'object'

class solid_motion_axis_origin_components_child(Group):
    """
    'child_object_type' of solid_motion_axis_origin_components.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'solid_motion_axis_origin_components_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class solid_motion_axis_origin_components(ListObject[solid_motion_axis_origin_components_child]):
    """
    'solid_motion_axis_origin_components' child.
    """
    _version = '222'
    fluent_name = 'solid-motion-axis-origin-components'
    _python_name = 'solid_motion_axis_origin_components'
    child_object_type = solid_motion_axis_origin_components_child
    return_type = 'object'

class solid_motion_axis_direction_components_child(Group):
    """
    'child_object_type' of solid_motion_axis_direction_components.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'solid_motion_axis_direction_components_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class solid_motion_axis_direction_components(ListObject[solid_motion_axis_direction_components_child]):
    """
    'solid_motion_axis_direction_components' child.
    """
    _version = '222'
    fluent_name = 'solid-motion-axis-direction-components'
    _python_name = 'solid_motion_axis_direction_components'
    child_object_type = solid_motion_axis_direction_components_child
    return_type = 'object'

class solid_udf_zmotion_name(String, AllowedValuesMixin):
    """
    'solid_udf_zmotion_name' child.
    """
    _version = '222'
    fluent_name = 'solid-udf-zmotion-name'
    _python_name = 'solid_udf_zmotion_name'
    return_type = 'object'

class radiating(Boolean, AllowedValuesMixin):
    """
    'radiating' child.
    """
    _version = '222'
    fluent_name = 'radiating?'
    _python_name = 'radiating'
    return_type = 'object'

class les_embedded(Boolean, AllowedValuesMixin):
    """
    'les_embedded' child.
    """
    _version = '222'
    fluent_name = 'les-embedded?'
    _python_name = 'les_embedded'
    return_type = 'object'

class contact_property(Boolean, AllowedValuesMixin):
    """
    'contact_property' child.
    """
    _version = '222'
    fluent_name = 'contact-property?'
    _python_name = 'contact_property'
    return_type = 'object'

class vapor_phase_realgas(Integer, AllowedValuesMixin):
    """
    'vapor_phase_realgas' child.
    """
    _version = '222'
    fluent_name = 'vapor-phase-realgas'
    _python_name = 'vapor_phase_realgas'
    return_type = 'object'

class laminar(Boolean, AllowedValuesMixin):
    """
    'laminar' child.
    """
    _version = '222'
    fluent_name = 'laminar?'
    _python_name = 'laminar'
    return_type = 'object'

class laminar_mut_zero(Boolean, AllowedValuesMixin):
    """
    'laminar_mut_zero' child.
    """
    _version = '222'
    fluent_name = 'laminar-mut-zero?'
    _python_name = 'laminar_mut_zero'
    return_type = 'object'

class les_embedded_spec(String, AllowedValuesMixin):
    """
    'les_embedded_spec' child.
    """
    _version = '222'
    fluent_name = 'les-embedded-spec'
    _python_name = 'les_embedded_spec'
    return_type = 'object'

class les_embedded_mom_scheme(String, AllowedValuesMixin):
    """
    'les_embedded_mom_scheme' child.
    """
    _version = '222'
    fluent_name = 'les-embedded-mom-scheme'
    _python_name = 'les_embedded_mom_scheme'
    return_type = 'object'

class les_embedded_c_wale(Real, AllowedValuesMixin):
    """
    'les_embedded_c_wale' child.
    """
    _version = '222'
    fluent_name = 'les-embedded-c-wale'
    _python_name = 'les_embedded_c_wale'
    return_type = 'object'

class les_embedded_c_smag(Real, AllowedValuesMixin):
    """
    'les_embedded_c_smag' child.
    """
    _version = '222'
    fluent_name = 'les-embedded-c-smag'
    _python_name = 'les_embedded_c_smag'
    return_type = 'object'

class glass(Boolean, AllowedValuesMixin):
    """
    'glass' child.
    """
    _version = '222'
    fluent_name = 'glass?'
    _python_name = 'glass'
    return_type = 'object'

class porous(Boolean, AllowedValuesMixin):
    """
    'porous' child.
    """
    _version = '222'
    fluent_name = 'porous?'
    _python_name = 'porous'
    return_type = 'object'

class conical(Boolean, AllowedValuesMixin):
    """
    'conical' child.
    """
    _version = '222'
    fluent_name = 'conical?'
    _python_name = 'conical'
    return_type = 'object'

class dir_spec_cond(String, AllowedValuesMixin):
    """
    'dir_spec_cond' child.
    """
    _version = '222'
    fluent_name = 'dir-spec-cond'
    _python_name = 'dir_spec_cond'
    return_type = 'object'

class cursys(Boolean, AllowedValuesMixin):
    """
    'cursys' child.
    """
    _version = '222'
    fluent_name = 'cursys?'
    _python_name = 'cursys'
    return_type = 'object'

class cursys_name(String, AllowedValuesMixin):
    """
    'cursys_name' child.
    """
    _version = '222'
    fluent_name = 'cursys-name'
    _python_name = 'cursys_name'
    return_type = 'object'

class direction_1_x(Group):
    """
    'direction_1_x' child.
    """
    _version = '222'
    fluent_name = 'direction-1-x'
    _python_name = 'direction_1_x'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class direction_1_y(Group):
    """
    'direction_1_y' child.
    """
    _version = '222'
    fluent_name = 'direction-1-y'
    _python_name = 'direction_1_y'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class direction_1_z(Group):
    """
    'direction_1_z' child.
    """
    _version = '222'
    fluent_name = 'direction-1-z'
    _python_name = 'direction_1_z'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class direction_2_x(Group):
    """
    'direction_2_x' child.
    """
    _version = '222'
    fluent_name = 'direction-2-x'
    _python_name = 'direction_2_x'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class direction_2_y(Group):
    """
    'direction_2_y' child.
    """
    _version = '222'
    fluent_name = 'direction-2-y'
    _python_name = 'direction_2_y'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class direction_2_z(Group):
    """
    'direction_2_z' child.
    """
    _version = '222'
    fluent_name = 'direction-2-z'
    _python_name = 'direction_2_z'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class cone_axis_x(Real, AllowedValuesMixin):
    """
    'cone_axis_x' child.
    """
    _version = '222'
    fluent_name = 'cone-axis-x'
    _python_name = 'cone_axis_x'
    return_type = 'object'

class cone_axis_y(Real, AllowedValuesMixin):
    """
    'cone_axis_y' child.
    """
    _version = '222'
    fluent_name = 'cone-axis-y'
    _python_name = 'cone_axis_y'
    return_type = 'object'

class cone_axis_z(Real, AllowedValuesMixin):
    """
    'cone_axis_z' child.
    """
    _version = '222'
    fluent_name = 'cone-axis-z'
    _python_name = 'cone_axis_z'
    return_type = 'object'

class cone_axis_pt_x(Real, AllowedValuesMixin):
    """
    'cone_axis_pt_x' child.
    """
    _version = '222'
    fluent_name = 'cone-axis-pt-x'
    _python_name = 'cone_axis_pt_x'
    return_type = 'object'

class cone_axis_pt_y(Real, AllowedValuesMixin):
    """
    'cone_axis_pt_y' child.
    """
    _version = '222'
    fluent_name = 'cone-axis-pt-y'
    _python_name = 'cone_axis_pt_y'
    return_type = 'object'

class cone_axis_pt_z(Real, AllowedValuesMixin):
    """
    'cone_axis_pt_z' child.
    """
    _version = '222'
    fluent_name = 'cone-axis-pt-z'
    _python_name = 'cone_axis_pt_z'
    return_type = 'object'

class cone_angle(Real, AllowedValuesMixin):
    """
    'cone_angle' child.
    """
    _version = '222'
    fluent_name = 'cone-angle'
    _python_name = 'cone_angle'
    return_type = 'object'

class rel_vel_resistance(Boolean, AllowedValuesMixin):
    """
    'rel_vel_resistance' child.
    """
    _version = '222'
    fluent_name = 'rel-vel-resistance?'
    _python_name = 'rel_vel_resistance'
    return_type = 'object'

class porous_r_1(Group):
    """
    'porous_r_1' child.
    """
    _version = '222'
    fluent_name = 'porous-r-1'
    _python_name = 'porous_r_1'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class porous_r_2(Group):
    """
    'porous_r_2' child.
    """
    _version = '222'
    fluent_name = 'porous-r-2'
    _python_name = 'porous_r_2'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class porous_r_3(Group):
    """
    'porous_r_3' child.
    """
    _version = '222'
    fluent_name = 'porous-r-3'
    _python_name = 'porous_r_3'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class alt_inertial_form(Boolean, AllowedValuesMixin):
    """
    'alt_inertial_form' child.
    """
    _version = '222'
    fluent_name = 'alt-inertial-form?'
    _python_name = 'alt_inertial_form'
    return_type = 'object'

class porous_c_1(Group):
    """
    'porous_c_1' child.
    """
    _version = '222'
    fluent_name = 'porous-c-1'
    _python_name = 'porous_c_1'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class porous_c_2(Group):
    """
    'porous_c_2' child.
    """
    _version = '222'
    fluent_name = 'porous-c-2'
    _python_name = 'porous_c_2'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class porous_c_3(Group):
    """
    'porous_c_3' child.
    """
    _version = '222'
    fluent_name = 'porous-c-3'
    _python_name = 'porous_c_3'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class c0(Real, AllowedValuesMixin):
    """
    'c0' child.
    """
    _version = '222'
    fluent_name = 'c0'
    _python_name = 'c0'
    return_type = 'object'

class c1(Real, AllowedValuesMixin):
    """
    'c1' child.
    """
    _version = '222'
    fluent_name = 'c1'
    _python_name = 'c1'
    return_type = 'object'

class porosity(Group):
    """
    'porosity' child.
    """
    _version = '222'
    fluent_name = 'porosity'
    _python_name = 'porosity'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class method(String, AllowedValuesMixin):
    """
    'method' child.
    """
    _version = '222'
    fluent_name = 'method'
    _python_name = 'method'
    return_type = 'object'

class function_of(String, AllowedValuesMixin):
    """
    'function_of' child.
    """
    _version = '222'
    fluent_name = 'function-of'
    _python_name = 'function_of'
    return_type = 'object'

class viscosity_ratio(Group):
    """
    'viscosity_ratio' child.
    """
    _version = '222'
    fluent_name = 'viscosity-ratio'
    _python_name = 'viscosity_ratio'
    child_names = ['method', 'number_of_coeff', 'function_of', 'coefficients', 'constant', 'piecewise_polynomial', 'piecewise_linear']
    _child_classes = dict(
        method=method,
        number_of_coeff=number_of_coeff,
        function_of=function_of,
        coefficients=coefficients,
        constant=constant,
        piecewise_polynomial=piecewise_polynomial,
        piecewise_linear=piecewise_linear,
    )
    return_type = 'object'

class none(Boolean, AllowedValuesMixin):
    """
    'none' child.
    """
    _version = '222'
    fluent_name = 'none?'
    _python_name = 'none'
    return_type = 'object'

class corey(Boolean, AllowedValuesMixin):
    """
    'corey' child.
    """
    _version = '222'
    fluent_name = 'corey?'
    _python_name = 'corey'
    return_type = 'object'

class stone_1(Boolean, AllowedValuesMixin):
    """
    'stone_1' child.
    """
    _version = '222'
    fluent_name = 'stone-1?'
    _python_name = 'stone_1'
    return_type = 'object'

class stone_2(Boolean, AllowedValuesMixin):
    """
    'stone_2' child.
    """
    _version = '222'
    fluent_name = 'stone-2?'
    _python_name = 'stone_2'
    return_type = 'object'

class rel_perm_limit_p1(Real, AllowedValuesMixin):
    """
    'rel_perm_limit_p1' child.
    """
    _version = '222'
    fluent_name = 'rel-perm-limit-p1'
    _python_name = 'rel_perm_limit_p1'
    return_type = 'object'

class rel_perm_limit_p2(Real, AllowedValuesMixin):
    """
    'rel_perm_limit_p2' child.
    """
    _version = '222'
    fluent_name = 'rel-perm-limit-p2'
    _python_name = 'rel_perm_limit_p2'
    return_type = 'object'

class ref_perm_p1(Real, AllowedValuesMixin):
    """
    'ref_perm_p1' child.
    """
    _version = '222'
    fluent_name = 'ref-perm-p1'
    _python_name = 'ref_perm_p1'
    return_type = 'object'

class exp_p1(Real, AllowedValuesMixin):
    """
    'exp_p1' child.
    """
    _version = '222'
    fluent_name = 'exp-p1'
    _python_name = 'exp_p1'
    return_type = 'object'

class res_sat_p1(Real, AllowedValuesMixin):
    """
    'res_sat_p1' child.
    """
    _version = '222'
    fluent_name = 'res-sat-p1'
    _python_name = 'res_sat_p1'
    return_type = 'object'

class ref_perm_p2(Real, AllowedValuesMixin):
    """
    'ref_perm_p2' child.
    """
    _version = '222'
    fluent_name = 'ref-perm-p2'
    _python_name = 'ref_perm_p2'
    return_type = 'object'

class exp_p2(Real, AllowedValuesMixin):
    """
    'exp_p2' child.
    """
    _version = '222'
    fluent_name = 'exp-p2'
    _python_name = 'exp_p2'
    return_type = 'object'

class res_sat_p2(Real, AllowedValuesMixin):
    """
    'res_sat_p2' child.
    """
    _version = '222'
    fluent_name = 'res-sat-p2'
    _python_name = 'res_sat_p2'
    return_type = 'object'

class ref_perm_p3(Real, AllowedValuesMixin):
    """
    'ref_perm_p3' child.
    """
    _version = '222'
    fluent_name = 'ref-perm-p3'
    _python_name = 'ref_perm_p3'
    return_type = 'object'

class exp_p3(Real, AllowedValuesMixin):
    """
    'exp_p3' child.
    """
    _version = '222'
    fluent_name = 'exp-p3'
    _python_name = 'exp_p3'
    return_type = 'object'

class res_sat_p3(Real, AllowedValuesMixin):
    """
    'res_sat_p3' child.
    """
    _version = '222'
    fluent_name = 'res-sat-p3'
    _python_name = 'res_sat_p3'
    return_type = 'object'

class capillary_pressure(Group):
    """
    'capillary_pressure' child.
    """
    _version = '222'
    fluent_name = 'capillary-pressure'
    _python_name = 'capillary_pressure'
    child_names = ['method', 'number_of_coeff', 'function_of', 'coefficients', 'constant', 'piecewise_polynomial', 'piecewise_linear']
    _child_classes = dict(
        method=method,
        number_of_coeff=number_of_coeff,
        function_of=function_of,
        coefficients=coefficients,
        constant=constant,
        piecewise_polynomial=piecewise_polynomial,
        piecewise_linear=piecewise_linear,
    )
    return_type = 'object'

class max_capillary_pressure(Real, AllowedValuesMixin):
    """
    'max_capillary_pressure' child.
    """
    _version = '222'
    fluent_name = 'max-capillary-pressure'
    _python_name = 'max_capillary_pressure'
    return_type = 'object'

class van_genuchten_pg(Real, AllowedValuesMixin):
    """
    'van_genuchten_pg' child.
    """
    _version = '222'
    fluent_name = 'van-genuchten-pg'
    _python_name = 'van_genuchten_pg'
    return_type = 'object'

class van_genuchten_ng(Real, AllowedValuesMixin):
    """
    'van_genuchten_ng' child.
    """
    _version = '222'
    fluent_name = 'van-genuchten-ng'
    _python_name = 'van_genuchten_ng'
    return_type = 'object'

class skjaeveland_nw_pc_coef(Real, AllowedValuesMixin):
    """
    'skjaeveland_nw_pc_coef' child.
    """
    _version = '222'
    fluent_name = 'skjaeveland-nw-pc-coef'
    _python_name = 'skjaeveland_nw_pc_coef'
    return_type = 'object'

class skjaeveland_nw_pc_pwr(Real, AllowedValuesMixin):
    """
    'skjaeveland_nw_pc_pwr' child.
    """
    _version = '222'
    fluent_name = 'skjaeveland-nw-pc-pwr'
    _python_name = 'skjaeveland_nw_pc_pwr'
    return_type = 'object'

class skjaeveland_wet_pc_coef(Real, AllowedValuesMixin):
    """
    'skjaeveland_wet_pc_coef' child.
    """
    _version = '222'
    fluent_name = 'skjaeveland-wet-pc-coef'
    _python_name = 'skjaeveland_wet_pc_coef'
    return_type = 'object'

class skjaeveland_wet_pc_pwr(Real, AllowedValuesMixin):
    """
    'skjaeveland_wet_pc_pwr' child.
    """
    _version = '222'
    fluent_name = 'skjaeveland-wet-pc-pwr'
    _python_name = 'skjaeveland_wet_pc_pwr'
    return_type = 'object'

class brooks_corey_pe(Real, AllowedValuesMixin):
    """
    'brooks_corey_pe' child.
    """
    _version = '222'
    fluent_name = 'brooks-corey-pe'
    _python_name = 'brooks_corey_pe'
    return_type = 'object'

class brooks_corey_ng(Real, AllowedValuesMixin):
    """
    'brooks_corey_ng' child.
    """
    _version = '222'
    fluent_name = 'brooks-corey-ng'
    _python_name = 'brooks_corey_ng'
    return_type = 'object'

class leverett_con_ang(Real, AllowedValuesMixin):
    """
    'leverett_con_ang' child.
    """
    _version = '222'
    fluent_name = 'leverett-con-ang'
    _python_name = 'leverett_con_ang'
    return_type = 'object'

class rp_cbox_p1(String, AllowedValuesMixin):
    """
    'rp_cbox_p1' child.
    """
    _version = '222'
    fluent_name = 'rp-cbox-p1'
    _python_name = 'rp_cbox_p1'
    return_type = 'object'

class rp_edit_p1(String, AllowedValuesMixin):
    """
    'rp_edit_p1' child.
    """
    _version = '222'
    fluent_name = 'rp-edit-p1'
    _python_name = 'rp_edit_p1'
    return_type = 'object'

class rel_perm_tabular_p1(Boolean, AllowedValuesMixin):
    """
    'rel_perm_tabular_p1' child.
    """
    _version = '222'
    fluent_name = 'rel-perm-tabular-p1?'
    _python_name = 'rel_perm_tabular_p1'
    return_type = 'object'

class rel_perm_table_p1(String, AllowedValuesMixin):
    """
    'rel_perm_table_p1' child.
    """
    _version = '222'
    fluent_name = 'rel-perm-table-p1'
    _python_name = 'rel_perm_table_p1'
    return_type = 'object'

class rel_perm_satw_p1(String, AllowedValuesMixin):
    """
    'rel_perm_satw_p1' child.
    """
    _version = '222'
    fluent_name = 'rel-perm-satw-p1'
    _python_name = 'rel_perm_satw_p1'
    return_type = 'object'

class rel_perm_rp_p1(String, AllowedValuesMixin):
    """
    'rel_perm_rp_p1' child.
    """
    _version = '222'
    fluent_name = 'rel-perm-rp-p1'
    _python_name = 'rel_perm_rp_p1'
    return_type = 'object'

class rp_cbox_p2(String, AllowedValuesMixin):
    """
    'rp_cbox_p2' child.
    """
    _version = '222'
    fluent_name = 'rp-cbox-p2'
    _python_name = 'rp_cbox_p2'
    return_type = 'object'

class rp_edit_p2(String, AllowedValuesMixin):
    """
    'rp_edit_p2' child.
    """
    _version = '222'
    fluent_name = 'rp-edit-p2'
    _python_name = 'rp_edit_p2'
    return_type = 'object'

class rel_perm_tabular_p2(Boolean, AllowedValuesMixin):
    """
    'rel_perm_tabular_p2' child.
    """
    _version = '222'
    fluent_name = 'rel-perm-tabular-p2?'
    _python_name = 'rel_perm_tabular_p2'
    return_type = 'object'

class rel_perm_table_p2(String, AllowedValuesMixin):
    """
    'rel_perm_table_p2' child.
    """
    _version = '222'
    fluent_name = 'rel-perm-table-p2'
    _python_name = 'rel_perm_table_p2'
    return_type = 'object'

class rel_perm_satw_p2(String, AllowedValuesMixin):
    """
    'rel_perm_satw_p2' child.
    """
    _version = '222'
    fluent_name = 'rel-perm-satw-p2'
    _python_name = 'rel_perm_satw_p2'
    return_type = 'object'

class rel_perm_rp_p2(String, AllowedValuesMixin):
    """
    'rel_perm_rp_p2' child.
    """
    _version = '222'
    fluent_name = 'rel-perm-rp-p2'
    _python_name = 'rel_perm_rp_p2'
    return_type = 'object'

class wetting_phase(String, AllowedValuesMixin):
    """
    'wetting_phase' child.
    """
    _version = '222'
    fluent_name = 'wetting-phase'
    _python_name = 'wetting_phase'
    return_type = 'object'

class non_wetting_phase(String, AllowedValuesMixin):
    """
    'non_wetting_phase' child.
    """
    _version = '222'
    fluent_name = 'non-wetting-phase'
    _python_name = 'non_wetting_phase'
    return_type = 'object'

class equib_thermal(Boolean, AllowedValuesMixin):
    """
    'equib_thermal' child.
    """
    _version = '222'
    fluent_name = 'equib-thermal?'
    _python_name = 'equib_thermal'
    return_type = 'object'

class non_equib_thermal(Boolean, AllowedValuesMixin):
    """
    'non_equib_thermal' child.
    """
    _version = '222'
    fluent_name = 'non-equib-thermal?'
    _python_name = 'non_equib_thermal'
    return_type = 'object'

class solid_material(String, AllowedValuesMixin):
    """
    'solid_material' child.
    """
    _version = '222'
    fluent_name = 'solid-material'
    _python_name = 'solid_material'
    return_type = 'object'

class area_density(Group):
    """
    'area_density' child.
    """
    _version = '222'
    fluent_name = 'area-density'
    _python_name = 'area_density'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class heat_transfer_coeff(Group):
    """
    'heat_transfer_coeff' child.
    """
    _version = '222'
    fluent_name = 'heat-transfer-coeff'
    _python_name = 'heat_transfer_coeff'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class fanzone(Boolean, AllowedValuesMixin):
    """
    'fanzone' child.
    """
    _version = '222'
    fluent_name = 'fanzone?'
    _python_name = 'fanzone'
    return_type = 'object'

class fan_zone_list(String, AllowedValuesMixin):
    """
    'fan_zone_list' child.
    """
    _version = '222'
    fluent_name = 'fan-zone-list'
    _python_name = 'fan_zone_list'
    return_type = 'object'

class fan_thickness(Real, AllowedValuesMixin):
    """
    'fan_thickness' child.
    """
    _version = '222'
    fluent_name = 'fan-thickness'
    _python_name = 'fan_thickness'
    return_type = 'object'

class fan_hub_rad(Real, AllowedValuesMixin):
    """
    'fan_hub_rad' child.
    """
    _version = '222'
    fluent_name = 'fan-hub-rad'
    _python_name = 'fan_hub_rad'
    return_type = 'object'

class fan_tip_rad(Real, AllowedValuesMixin):
    """
    'fan_tip_rad' child.
    """
    _version = '222'
    fluent_name = 'fan-tip-rad'
    _python_name = 'fan_tip_rad'
    return_type = 'object'

class fan_x_origin(Real, AllowedValuesMixin):
    """
    'fan_x_origin' child.
    """
    _version = '222'
    fluent_name = 'fan-x-origin'
    _python_name = 'fan_x_origin'
    return_type = 'object'

class fan_y_origin(Real, AllowedValuesMixin):
    """
    'fan_y_origin' child.
    """
    _version = '222'
    fluent_name = 'fan-y-origin'
    _python_name = 'fan_y_origin'
    return_type = 'object'

class fan_z_origin(Real, AllowedValuesMixin):
    """
    'fan_z_origin' child.
    """
    _version = '222'
    fluent_name = 'fan-z-origin'
    _python_name = 'fan_z_origin'
    return_type = 'object'

class fan_rot_dir(String, AllowedValuesMixin):
    """
    'fan_rot_dir' child.
    """
    _version = '222'
    fluent_name = 'fan-rot-dir'
    _python_name = 'fan_rot_dir'
    return_type = 'object'

class fan_opert_angvel(Real, AllowedValuesMixin):
    """
    'fan_opert_angvel' child.
    """
    _version = '222'
    fluent_name = 'fan-opert-angvel'
    _python_name = 'fan_opert_angvel'
    return_type = 'object'

class fan_inflection_point(Real, AllowedValuesMixin):
    """
    'fan_inflection_point' child.
    """
    _version = '222'
    fluent_name = 'fan-inflection-point'
    _python_name = 'fan_inflection_point'
    return_type = 'object'

class limit_flow_fan(Boolean, AllowedValuesMixin):
    """
    'limit_flow_fan' child.
    """
    _version = '222'
    fluent_name = 'limit-flow-fan'
    _python_name = 'limit_flow_fan'
    return_type = 'object'

class max_flow_rate(Real, AllowedValuesMixin):
    """
    'max_flow_rate' child.
    """
    _version = '222'
    fluent_name = 'max-flow-rate'
    _python_name = 'max_flow_rate'
    return_type = 'object'

class min_flow_rate(Real, AllowedValuesMixin):
    """
    'min_flow_rate' child.
    """
    _version = '222'
    fluent_name = 'min-flow-rate'
    _python_name = 'min_flow_rate'
    return_type = 'object'

class tan_source_term(Boolean, AllowedValuesMixin):
    """
    'tan_source_term' child.
    """
    _version = '222'
    fluent_name = 'tan-source-term'
    _python_name = 'tan_source_term'
    return_type = 'object'

class rad_source_term(Boolean, AllowedValuesMixin):
    """
    'rad_source_term' child.
    """
    _version = '222'
    fluent_name = 'rad-source-term'
    _python_name = 'rad_source_term'
    return_type = 'object'

class axial_source_term(Boolean, AllowedValuesMixin):
    """
    'axial_source_term' child.
    """
    _version = '222'
    fluent_name = 'axial-source-term'
    _python_name = 'axial_source_term'
    return_type = 'object'

class fan_axial_source_method(String, AllowedValuesMixin):
    """
    'fan_axial_source_method' child.
    """
    _version = '222'
    fluent_name = 'fan-axial-source-method'
    _python_name = 'fan_axial_source_method'
    return_type = 'object'

class fan_pre_jump(Real, AllowedValuesMixin):
    """
    'fan_pre_jump' child.
    """
    _version = '222'
    fluent_name = 'fan-pre-jump'
    _python_name = 'fan_pre_jump'
    return_type = 'object'

class fan_curve_fit(String, AllowedValuesMixin):
    """
    'fan_curve_fit' child.
    """
    _version = '222'
    fluent_name = 'fan-curve-fit'
    _python_name = 'fan_curve_fit'
    return_type = 'object'

class fan_poly_order(Real, AllowedValuesMixin):
    """
    'fan_poly_order' child.
    """
    _version = '222'
    fluent_name = 'fan-poly-order'
    _python_name = 'fan_poly_order'
    return_type = 'object'

class fan_ini_flow(Real, AllowedValuesMixin):
    """
    'fan_ini_flow' child.
    """
    _version = '222'
    fluent_name = 'fan-ini-flow'
    _python_name = 'fan_ini_flow'
    return_type = 'object'

class fan_test_angvel(Real, AllowedValuesMixin):
    """
    'fan_test_angvel' child.
    """
    _version = '222'
    fluent_name = 'fan-test-angvel'
    _python_name = 'fan_test_angvel'
    return_type = 'object'

class fan_test_temp(Real, AllowedValuesMixin):
    """
    'fan_test_temp' child.
    """
    _version = '222'
    fluent_name = 'fan-test-temp'
    _python_name = 'fan_test_temp'
    return_type = 'object'

class read_fan_curve(String, AllowedValuesMixin):
    """
    'read_fan_curve' child.
    """
    _version = '222'
    fluent_name = 'read-fan-curve'
    _python_name = 'read_fan_curve'
    return_type = 'object'

class reaction_mechs_1(String, AllowedValuesMixin):
    """
    'reaction_mechs' child.
    """
    _version = '222'
    fluent_name = 'reaction-mechs'
    _python_name = 'reaction_mechs'
    return_type = 'object'

class react(Boolean, AllowedValuesMixin):
    """
    'react' child.
    """
    _version = '222'
    fluent_name = 'react?'
    _python_name = 'react'
    return_type = 'object'

class surface_volume_ratio(Real, AllowedValuesMixin):
    """
    'surface_volume_ratio' child.
    """
    _version = '222'
    fluent_name = 'surface-volume-ratio'
    _python_name = 'surface_volume_ratio'
    return_type = 'object'

class electrolyte(Boolean, AllowedValuesMixin):
    """
    'electrolyte' child.
    """
    _version = '222'
    fluent_name = 'electrolyte?'
    _python_name = 'electrolyte'
    return_type = 'object'

class mp_compressive_beta_max(Real, AllowedValuesMixin):
    """
    'mp_compressive_beta_max' child.
    """
    _version = '222'
    fluent_name = 'mp-compressive-beta-max'
    _python_name = 'mp_compressive_beta_max'
    return_type = 'object'

class mp_boiling_zone(Boolean, AllowedValuesMixin):
    """
    'mp_boiling_zone' child.
    """
    _version = '222'
    fluent_name = 'mp-boiling-zone?'
    _python_name = 'mp_boiling_zone'
    return_type = 'object'

class numerical_beach(Boolean, AllowedValuesMixin):
    """
    'numerical_beach' child.
    """
    _version = '222'
    fluent_name = 'numerical-beach?'
    _python_name = 'numerical_beach'
    return_type = 'object'

class beach_id(Integer, AllowedValuesMixin):
    """
    'beach_id' child.
    """
    _version = '222'
    fluent_name = 'beach-id'
    _python_name = 'beach_id'
    return_type = 'object'

class beach_multi_dir(Boolean, AllowedValuesMixin):
    """
    'beach_multi_dir' child.
    """
    _version = '222'
    fluent_name = 'beach-multi-dir?'
    _python_name = 'beach_multi_dir'
    return_type = 'object'

class beach_damp_type(String, AllowedValuesMixin):
    """
    'beach_damp_type' child.
    """
    _version = '222'
    fluent_name = 'beach-damp-type'
    _python_name = 'beach_damp_type'
    return_type = 'object'

class beach_inlet_bndr(String, AllowedValuesMixin):
    """
    'beach_inlet_bndr' child.
    """
    _version = '222'
    fluent_name = 'beach-inlet-bndr'
    _python_name = 'beach_inlet_bndr'
    return_type = 'object'

class beach_fs_level(Real, AllowedValuesMixin):
    """
    'beach_fs_level' child.
    """
    _version = '222'
    fluent_name = 'beach-fs-level'
    _python_name = 'beach_fs_level'
    return_type = 'object'

class beach_bottom_level(Real, AllowedValuesMixin):
    """
    'beach_bottom_level' child.
    """
    _version = '222'
    fluent_name = 'beach-bottom-level'
    _python_name = 'beach_bottom_level'
    return_type = 'object'

class beach_dir_ni(Real, AllowedValuesMixin):
    """
    'beach_dir_ni' child.
    """
    _version = '222'
    fluent_name = 'beach-dir-ni'
    _python_name = 'beach_dir_ni'
    return_type = 'object'

class beach_dir_nj(Real, AllowedValuesMixin):
    """
    'beach_dir_nj' child.
    """
    _version = '222'
    fluent_name = 'beach-dir-nj'
    _python_name = 'beach_dir_nj'
    return_type = 'object'

class beach_dir_nk(Real, AllowedValuesMixin):
    """
    'beach_dir_nk' child.
    """
    _version = '222'
    fluent_name = 'beach-dir-nk'
    _python_name = 'beach_dir_nk'
    return_type = 'object'

class beach_damp_len_spec(String, AllowedValuesMixin):
    """
    'beach_damp_len_spec' child.
    """
    _version = '222'
    fluent_name = 'beach-damp-len-spec'
    _python_name = 'beach_damp_len_spec'
    return_type = 'object'

class beach_wave_len(Real, AllowedValuesMixin):
    """
    'beach_wave_len' child.
    """
    _version = '222'
    fluent_name = 'beach-wave-len'
    _python_name = 'beach_wave_len'
    return_type = 'object'

class beach_len_factor(Real, AllowedValuesMixin):
    """
    'beach_len_factor' child.
    """
    _version = '222'
    fluent_name = 'beach-len-factor'
    _python_name = 'beach_len_factor'
    return_type = 'object'

class beach_start_point(Real, AllowedValuesMixin):
    """
    'beach_start_point' child.
    """
    _version = '222'
    fluent_name = 'beach-start-point'
    _python_name = 'beach_start_point'
    return_type = 'object'

class beach_end_point(Real, AllowedValuesMixin):
    """
    'beach_end_point' child.
    """
    _version = '222'
    fluent_name = 'beach-end-point'
    _python_name = 'beach_end_point'
    return_type = 'object'

class ni(Real, AllowedValuesMixin):
    """
    'ni' child.
    """
    _version = '222'
    fluent_name = 'ni'
    _python_name = 'ni'
    return_type = 'object'

class nj(Real, AllowedValuesMixin):
    """
    'nj' child.
    """
    _version = '222'
    fluent_name = 'nj'
    _python_name = 'nj'
    return_type = 'object'

class nk(Real, AllowedValuesMixin):
    """
    'nk' child.
    """
    _version = '222'
    fluent_name = 'nk'
    _python_name = 'nk'
    return_type = 'object'

class xe(Real, AllowedValuesMixin):
    """
    'xe' child.
    """
    _version = '222'
    fluent_name = 'xe'
    _python_name = 'xe'
    return_type = 'object'

class len(Real, AllowedValuesMixin):
    """
    'len' child.
    """
    _version = '222'
    fluent_name = 'len'
    _python_name = 'len'
    return_type = 'object'

class beach_dir_list_child(Group):
    """
    'child_object_type' of beach_dir_list.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'beach_dir_list_child'
    child_names = ['ni', 'nj', 'nk', 'xe', 'len']
    _child_classes = dict(
        ni=ni,
        nj=nj,
        nk=nk,
        xe=xe,
        len=len,
    )
    return_type = 'object'

class beach_dir_list(ListObject[beach_dir_list_child]):
    """
    'beach_dir_list' child.
    """
    _version = '222'
    fluent_name = 'beach-dir-list'
    _python_name = 'beach_dir_list'
    child_object_type = beach_dir_list_child
    return_type = 'object'

class beach_damp_relative(Boolean, AllowedValuesMixin):
    """
    'beach_damp_relative' child.
    """
    _version = '222'
    fluent_name = 'beach-damp-relative?'
    _python_name = 'beach_damp_relative'
    return_type = 'object'

class beach_damp_resist_lin(Real, AllowedValuesMixin):
    """
    'beach_damp_resist_lin' child.
    """
    _version = '222'
    fluent_name = 'beach-damp-resist-lin'
    _python_name = 'beach_damp_resist_lin'
    return_type = 'object'

class beach_damp_resist(Real, AllowedValuesMixin):
    """
    'beach_damp_resist' child.
    """
    _version = '222'
    fluent_name = 'beach-damp-resist'
    _python_name = 'beach_damp_resist'
    return_type = 'object'

class porous_structure(Boolean, AllowedValuesMixin):
    """
    'porous_structure' child.
    """
    _version = '222'
    fluent_name = 'porous-structure?'
    _python_name = 'porous_structure'
    return_type = 'object'

class structure_material(String, AllowedValuesMixin):
    """
    'structure_material' child.
    """
    _version = '222'
    fluent_name = 'structure-material'
    _python_name = 'structure_material'
    return_type = 'object'

class anisotropic_spe_diff(Boolean, AllowedValuesMixin):
    """
    'anisotropic_spe_diff' child.
    """
    _version = '222'
    fluent_name = 'anisotropic-spe-diff?'
    _python_name = 'anisotropic_spe_diff'
    return_type = 'object'

class spe_diff_xx(Real, AllowedValuesMixin):
    """
    'spe_diff_xx' child.
    """
    _version = '222'
    fluent_name = 'spe-diff-xx'
    _python_name = 'spe_diff_xx'
    return_type = 'object'

class spe_diff_xy(Real, AllowedValuesMixin):
    """
    'spe_diff_xy' child.
    """
    _version = '222'
    fluent_name = 'spe-diff-xy'
    _python_name = 'spe_diff_xy'
    return_type = 'object'

class spe_diff_xz(Real, AllowedValuesMixin):
    """
    'spe_diff_xz' child.
    """
    _version = '222'
    fluent_name = 'spe-diff-xz'
    _python_name = 'spe_diff_xz'
    return_type = 'object'

class spe_diff_yx(Real, AllowedValuesMixin):
    """
    'spe_diff_yx' child.
    """
    _version = '222'
    fluent_name = 'spe-diff-yx'
    _python_name = 'spe_diff_yx'
    return_type = 'object'

class spe_diff_yy(Real, AllowedValuesMixin):
    """
    'spe_diff_yy' child.
    """
    _version = '222'
    fluent_name = 'spe-diff-yy'
    _python_name = 'spe_diff_yy'
    return_type = 'object'

class spe_diff_yz(Real, AllowedValuesMixin):
    """
    'spe_diff_yz' child.
    """
    _version = '222'
    fluent_name = 'spe-diff-yz'
    _python_name = 'spe_diff_yz'
    return_type = 'object'

class spe_diff_zx(Real, AllowedValuesMixin):
    """
    'spe_diff_zx' child.
    """
    _version = '222'
    fluent_name = 'spe-diff-zx'
    _python_name = 'spe_diff_zx'
    return_type = 'object'

class spe_diff_zy(Real, AllowedValuesMixin):
    """
    'spe_diff_zy' child.
    """
    _version = '222'
    fluent_name = 'spe-diff-zy'
    _python_name = 'spe_diff_zy'
    return_type = 'object'

class spe_diff_zz(Real, AllowedValuesMixin):
    """
    'spe_diff_zz' child.
    """
    _version = '222'
    fluent_name = 'spe-diff-zz'
    _python_name = 'spe_diff_zz'
    return_type = 'object'

class phase_child(Group):
    """
    'child_object_type' of phase.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'phase_child'
    child_names = ['material', 'sources', 'source_terms', 'fixed', 'cylindrical_fixed_var', 'fixes', 'motion_spec', 'relative_to_thread', 'omega', 'axis_origin_component', 'axis_direction_component', 'udf_zmotion_name', 'mrf_motion', 'mrf_relative_to_thread', 'mrf_omega', 'reference_frame_velocity_components', 'reference_frame_axis_origin_components', 'reference_frame_axis_direction_components', 'mrf_udf_zmotion_name', 'mgrid_enable_transient', 'mgrid_motion', 'mgrid_relative_to_thread', 'mgrid_omega', 'moving_mesh_velocity_components', 'moving_mesh_axis_origin_components', 'mgrid_udf_zmotion_name', 'solid_motion', 'solid_relative_to_thread', 'solid_omega', 'solid_motion_velocity_components', 'solid_motion_axis_origin_components', 'solid_motion_axis_direction_components', 'solid_udf_zmotion_name', 'radiating', 'les_embedded', 'contact_property', 'vapor_phase_realgas', 'laminar', 'laminar_mut_zero', 'les_embedded_spec', 'les_embedded_mom_scheme', 'les_embedded_c_wale', 'les_embedded_c_smag', 'glass', 'porous', 'conical', 'dir_spec_cond', 'cursys', 'cursys_name', 'direction_1_x', 'direction_1_y', 'direction_1_z', 'direction_2_x', 'direction_2_y', 'direction_2_z', 'cone_axis_x', 'cone_axis_y', 'cone_axis_z', 'cone_axis_pt_x', 'cone_axis_pt_y', 'cone_axis_pt_z', 'cone_angle', 'rel_vel_resistance', 'porous_r_1', 'porous_r_2', 'porous_r_3', 'alt_inertial_form', 'porous_c_1', 'porous_c_2', 'porous_c_3', 'c0', 'c1', 'porosity', 'viscosity_ratio', 'none', 'corey', 'stone_1', 'stone_2', 'rel_perm_limit_p1', 'rel_perm_limit_p2', 'ref_perm_p1', 'exp_p1', 'res_sat_p1', 'ref_perm_p2', 'exp_p2', 'res_sat_p2', 'ref_perm_p3', 'exp_p3', 'res_sat_p3', 'capillary_pressure', 'max_capillary_pressure', 'van_genuchten_pg', 'van_genuchten_ng', 'skjaeveland_nw_pc_coef', 'skjaeveland_nw_pc_pwr', 'skjaeveland_wet_pc_coef', 'skjaeveland_wet_pc_pwr', 'brooks_corey_pe', 'brooks_corey_ng', 'leverett_con_ang', 'rp_cbox_p1', 'rp_edit_p1', 'rel_perm_tabular_p1', 'rel_perm_table_p1', 'rel_perm_satw_p1', 'rel_perm_rp_p1', 'rp_cbox_p2', 'rp_edit_p2', 'rel_perm_tabular_p2', 'rel_perm_table_p2', 'rel_perm_satw_p2', 'rel_perm_rp_p2', 'wetting_phase', 'non_wetting_phase', 'equib_thermal', 'non_equib_thermal', 'solid_material', 'area_density', 'heat_transfer_coeff', 'fanzone', 'fan_zone_list', 'fan_thickness', 'fan_hub_rad', 'fan_tip_rad', 'fan_x_origin', 'fan_y_origin', 'fan_z_origin', 'fan_rot_dir', 'fan_opert_angvel', 'fan_inflection_point', 'limit_flow_fan', 'max_flow_rate', 'min_flow_rate', 'tan_source_term', 'rad_source_term', 'axial_source_term', 'fan_axial_source_method', 'fan_pre_jump', 'fan_curve_fit', 'fan_poly_order', 'fan_ini_flow', 'fan_test_angvel', 'fan_test_temp', 'read_fan_curve', 'reaction_mechs', 'react', 'surface_volume_ratio', 'electrolyte', 'mp_compressive_beta_max', 'mp_boiling_zone', 'numerical_beach', 'beach_id', 'beach_multi_dir', 'beach_damp_type', 'beach_inlet_bndr', 'beach_fs_level', 'beach_bottom_level', 'beach_dir_ni', 'beach_dir_nj', 'beach_dir_nk', 'beach_damp_len_spec', 'beach_wave_len', 'beach_len_factor', 'beach_start_point', 'beach_end_point', 'beach_dir_list', 'beach_damp_relative', 'beach_damp_resist_lin', 'beach_damp_resist', 'porous_structure', 'structure_material', 'anisotropic_spe_diff', 'spe_diff_xx', 'spe_diff_xy', 'spe_diff_xz', 'spe_diff_yx', 'spe_diff_yy', 'spe_diff_yz', 'spe_diff_zx', 'spe_diff_zy', 'spe_diff_zz']
    _child_classes = dict(
        material=material,
        sources=sources,
        source_terms=source_terms,
        fixed=fixed,
        cylindrical_fixed_var=cylindrical_fixed_var,
        fixes=fixes,
        motion_spec=motion_spec,
        relative_to_thread=relative_to_thread,
        omega=omega,
        axis_origin_component=axis_origin_component,
        axis_direction_component=axis_direction_component,
        udf_zmotion_name=udf_zmotion_name,
        mrf_motion=mrf_motion,
        mrf_relative_to_thread=mrf_relative_to_thread,
        mrf_omega=mrf_omega,
        reference_frame_velocity_components=reference_frame_velocity_components,
        reference_frame_axis_origin_components=reference_frame_axis_origin_components,
        reference_frame_axis_direction_components=reference_frame_axis_direction_components,
        mrf_udf_zmotion_name=mrf_udf_zmotion_name,
        mgrid_enable_transient=mgrid_enable_transient,
        mgrid_motion=mgrid_motion,
        mgrid_relative_to_thread=mgrid_relative_to_thread,
        mgrid_omega=mgrid_omega,
        moving_mesh_velocity_components=moving_mesh_velocity_components,
        moving_mesh_axis_origin_components=moving_mesh_axis_origin_components,
        mgrid_udf_zmotion_name=mgrid_udf_zmotion_name,
        solid_motion=solid_motion,
        solid_relative_to_thread=solid_relative_to_thread,
        solid_omega=solid_omega,
        solid_motion_velocity_components=solid_motion_velocity_components,
        solid_motion_axis_origin_components=solid_motion_axis_origin_components,
        solid_motion_axis_direction_components=solid_motion_axis_direction_components,
        solid_udf_zmotion_name=solid_udf_zmotion_name,
        radiating=radiating,
        les_embedded=les_embedded,
        contact_property=contact_property,
        vapor_phase_realgas=vapor_phase_realgas,
        laminar=laminar,
        laminar_mut_zero=laminar_mut_zero,
        les_embedded_spec=les_embedded_spec,
        les_embedded_mom_scheme=les_embedded_mom_scheme,
        les_embedded_c_wale=les_embedded_c_wale,
        les_embedded_c_smag=les_embedded_c_smag,
        glass=glass,
        porous=porous,
        conical=conical,
        dir_spec_cond=dir_spec_cond,
        cursys=cursys,
        cursys_name=cursys_name,
        direction_1_x=direction_1_x,
        direction_1_y=direction_1_y,
        direction_1_z=direction_1_z,
        direction_2_x=direction_2_x,
        direction_2_y=direction_2_y,
        direction_2_z=direction_2_z,
        cone_axis_x=cone_axis_x,
        cone_axis_y=cone_axis_y,
        cone_axis_z=cone_axis_z,
        cone_axis_pt_x=cone_axis_pt_x,
        cone_axis_pt_y=cone_axis_pt_y,
        cone_axis_pt_z=cone_axis_pt_z,
        cone_angle=cone_angle,
        rel_vel_resistance=rel_vel_resistance,
        porous_r_1=porous_r_1,
        porous_r_2=porous_r_2,
        porous_r_3=porous_r_3,
        alt_inertial_form=alt_inertial_form,
        porous_c_1=porous_c_1,
        porous_c_2=porous_c_2,
        porous_c_3=porous_c_3,
        c0=c0,
        c1=c1,
        porosity=porosity,
        viscosity_ratio=viscosity_ratio,
        none=none,
        corey=corey,
        stone_1=stone_1,
        stone_2=stone_2,
        rel_perm_limit_p1=rel_perm_limit_p1,
        rel_perm_limit_p2=rel_perm_limit_p2,
        ref_perm_p1=ref_perm_p1,
        exp_p1=exp_p1,
        res_sat_p1=res_sat_p1,
        ref_perm_p2=ref_perm_p2,
        exp_p2=exp_p2,
        res_sat_p2=res_sat_p2,
        ref_perm_p3=ref_perm_p3,
        exp_p3=exp_p3,
        res_sat_p3=res_sat_p3,
        capillary_pressure=capillary_pressure,
        max_capillary_pressure=max_capillary_pressure,
        van_genuchten_pg=van_genuchten_pg,
        van_genuchten_ng=van_genuchten_ng,
        skjaeveland_nw_pc_coef=skjaeveland_nw_pc_coef,
        skjaeveland_nw_pc_pwr=skjaeveland_nw_pc_pwr,
        skjaeveland_wet_pc_coef=skjaeveland_wet_pc_coef,
        skjaeveland_wet_pc_pwr=skjaeveland_wet_pc_pwr,
        brooks_corey_pe=brooks_corey_pe,
        brooks_corey_ng=brooks_corey_ng,
        leverett_con_ang=leverett_con_ang,
        rp_cbox_p1=rp_cbox_p1,
        rp_edit_p1=rp_edit_p1,
        rel_perm_tabular_p1=rel_perm_tabular_p1,
        rel_perm_table_p1=rel_perm_table_p1,
        rel_perm_satw_p1=rel_perm_satw_p1,
        rel_perm_rp_p1=rel_perm_rp_p1,
        rp_cbox_p2=rp_cbox_p2,
        rp_edit_p2=rp_edit_p2,
        rel_perm_tabular_p2=rel_perm_tabular_p2,
        rel_perm_table_p2=rel_perm_table_p2,
        rel_perm_satw_p2=rel_perm_satw_p2,
        rel_perm_rp_p2=rel_perm_rp_p2,
        wetting_phase=wetting_phase,
        non_wetting_phase=non_wetting_phase,
        equib_thermal=equib_thermal,
        non_equib_thermal=non_equib_thermal,
        solid_material=solid_material,
        area_density=area_density,
        heat_transfer_coeff=heat_transfer_coeff,
        fanzone=fanzone,
        fan_zone_list=fan_zone_list,
        fan_thickness=fan_thickness,
        fan_hub_rad=fan_hub_rad,
        fan_tip_rad=fan_tip_rad,
        fan_x_origin=fan_x_origin,
        fan_y_origin=fan_y_origin,
        fan_z_origin=fan_z_origin,
        fan_rot_dir=fan_rot_dir,
        fan_opert_angvel=fan_opert_angvel,
        fan_inflection_point=fan_inflection_point,
        limit_flow_fan=limit_flow_fan,
        max_flow_rate=max_flow_rate,
        min_flow_rate=min_flow_rate,
        tan_source_term=tan_source_term,
        rad_source_term=rad_source_term,
        axial_source_term=axial_source_term,
        fan_axial_source_method=fan_axial_source_method,
        fan_pre_jump=fan_pre_jump,
        fan_curve_fit=fan_curve_fit,
        fan_poly_order=fan_poly_order,
        fan_ini_flow=fan_ini_flow,
        fan_test_angvel=fan_test_angvel,
        fan_test_temp=fan_test_temp,
        read_fan_curve=read_fan_curve,
        reaction_mechs=reaction_mechs_1,
        react=react,
        surface_volume_ratio=surface_volume_ratio,
        electrolyte=electrolyte,
        mp_compressive_beta_max=mp_compressive_beta_max,
        mp_boiling_zone=mp_boiling_zone,
        numerical_beach=numerical_beach,
        beach_id=beach_id,
        beach_multi_dir=beach_multi_dir,
        beach_damp_type=beach_damp_type,
        beach_inlet_bndr=beach_inlet_bndr,
        beach_fs_level=beach_fs_level,
        beach_bottom_level=beach_bottom_level,
        beach_dir_ni=beach_dir_ni,
        beach_dir_nj=beach_dir_nj,
        beach_dir_nk=beach_dir_nk,
        beach_damp_len_spec=beach_damp_len_spec,
        beach_wave_len=beach_wave_len,
        beach_len_factor=beach_len_factor,
        beach_start_point=beach_start_point,
        beach_end_point=beach_end_point,
        beach_dir_list=beach_dir_list,
        beach_damp_relative=beach_damp_relative,
        beach_damp_resist_lin=beach_damp_resist_lin,
        beach_damp_resist=beach_damp_resist,
        porous_structure=porous_structure,
        structure_material=structure_material,
        anisotropic_spe_diff=anisotropic_spe_diff,
        spe_diff_xx=spe_diff_xx,
        spe_diff_xy=spe_diff_xy,
        spe_diff_xz=spe_diff_xz,
        spe_diff_yx=spe_diff_yx,
        spe_diff_yy=spe_diff_yy,
        spe_diff_yz=spe_diff_yz,
        spe_diff_zx=spe_diff_zx,
        spe_diff_zy=spe_diff_zy,
        spe_diff_zz=spe_diff_zz,
    )
    return_type = 'object'

class phase(NamedObject[phase_child], CreatableNamedObjectMixinOld[phase_child]):
    """
    'phase' child.
    """
    _version = '222'
    fluent_name = 'phase'
    _python_name = 'phase'
    child_object_type = phase_child
    return_type = 'object'

class fluid_1_child(Group):
    """
    'child_object_type' of fluid.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'fluid_child'
    child_names = ['phase', 'material', 'sources', 'source_terms', 'fixed', 'cylindrical_fixed_var', 'fixes', 'motion_spec', 'relative_to_thread', 'omega', 'axis_origin_component', 'axis_direction_component', 'udf_zmotion_name', 'mrf_motion', 'mrf_relative_to_thread', 'mrf_omega', 'reference_frame_velocity_components', 'reference_frame_axis_origin_components', 'reference_frame_axis_direction_components', 'mrf_udf_zmotion_name', 'mgrid_enable_transient', 'mgrid_motion', 'mgrid_relative_to_thread', 'mgrid_omega', 'moving_mesh_velocity_components', 'moving_mesh_axis_origin_components', 'mgrid_udf_zmotion_name', 'solid_motion', 'solid_relative_to_thread', 'solid_omega', 'solid_motion_velocity_components', 'solid_motion_axis_origin_components', 'solid_motion_axis_direction_components', 'solid_udf_zmotion_name', 'radiating', 'les_embedded', 'contact_property', 'vapor_phase_realgas', 'laminar', 'laminar_mut_zero', 'les_embedded_spec', 'les_embedded_mom_scheme', 'les_embedded_c_wale', 'les_embedded_c_smag', 'glass', 'porous', 'conical', 'dir_spec_cond', 'cursys', 'cursys_name', 'direction_1_x', 'direction_1_y', 'direction_1_z', 'direction_2_x', 'direction_2_y', 'direction_2_z', 'cone_axis_x', 'cone_axis_y', 'cone_axis_z', 'cone_axis_pt_x', 'cone_axis_pt_y', 'cone_axis_pt_z', 'cone_angle', 'rel_vel_resistance', 'porous_r_1', 'porous_r_2', 'porous_r_3', 'alt_inertial_form', 'porous_c_1', 'porous_c_2', 'porous_c_3', 'c0', 'c1', 'porosity', 'viscosity_ratio', 'none', 'corey', 'stone_1', 'stone_2', 'rel_perm_limit_p1', 'rel_perm_limit_p2', 'ref_perm_p1', 'exp_p1', 'res_sat_p1', 'ref_perm_p2', 'exp_p2', 'res_sat_p2', 'ref_perm_p3', 'exp_p3', 'res_sat_p3', 'capillary_pressure', 'max_capillary_pressure', 'van_genuchten_pg', 'van_genuchten_ng', 'skjaeveland_nw_pc_coef', 'skjaeveland_nw_pc_pwr', 'skjaeveland_wet_pc_coef', 'skjaeveland_wet_pc_pwr', 'brooks_corey_pe', 'brooks_corey_ng', 'leverett_con_ang', 'rp_cbox_p1', 'rp_edit_p1', 'rel_perm_tabular_p1', 'rel_perm_table_p1', 'rel_perm_satw_p1', 'rel_perm_rp_p1', 'rp_cbox_p2', 'rp_edit_p2', 'rel_perm_tabular_p2', 'rel_perm_table_p2', 'rel_perm_satw_p2', 'rel_perm_rp_p2', 'wetting_phase', 'non_wetting_phase', 'equib_thermal', 'non_equib_thermal', 'solid_material', 'area_density', 'heat_transfer_coeff', 'fanzone', 'fan_zone_list', 'fan_thickness', 'fan_hub_rad', 'fan_tip_rad', 'fan_x_origin', 'fan_y_origin', 'fan_z_origin', 'fan_rot_dir', 'fan_opert_angvel', 'fan_inflection_point', 'limit_flow_fan', 'max_flow_rate', 'min_flow_rate', 'tan_source_term', 'rad_source_term', 'axial_source_term', 'fan_axial_source_method', 'fan_pre_jump', 'fan_curve_fit', 'fan_poly_order', 'fan_ini_flow', 'fan_test_angvel', 'fan_test_temp', 'read_fan_curve', 'reaction_mechs', 'react', 'surface_volume_ratio', 'electrolyte', 'mp_compressive_beta_max', 'mp_boiling_zone', 'numerical_beach', 'beach_id', 'beach_multi_dir', 'beach_damp_type', 'beach_inlet_bndr', 'beach_fs_level', 'beach_bottom_level', 'beach_dir_ni', 'beach_dir_nj', 'beach_dir_nk', 'beach_damp_len_spec', 'beach_wave_len', 'beach_len_factor', 'beach_start_point', 'beach_end_point', 'beach_dir_list', 'beach_damp_relative', 'beach_damp_resist_lin', 'beach_damp_resist', 'porous_structure', 'structure_material', 'anisotropic_spe_diff', 'spe_diff_xx', 'spe_diff_xy', 'spe_diff_xz', 'spe_diff_yx', 'spe_diff_yy', 'spe_diff_yz', 'spe_diff_zx', 'spe_diff_zy', 'spe_diff_zz']
    _child_classes = dict(
        phase=phase,
        material=material,
        sources=sources,
        source_terms=source_terms,
        fixed=fixed,
        cylindrical_fixed_var=cylindrical_fixed_var,
        fixes=fixes,
        motion_spec=motion_spec,
        relative_to_thread=relative_to_thread,
        omega=omega,
        axis_origin_component=axis_origin_component,
        axis_direction_component=axis_direction_component,
        udf_zmotion_name=udf_zmotion_name,
        mrf_motion=mrf_motion,
        mrf_relative_to_thread=mrf_relative_to_thread,
        mrf_omega=mrf_omega,
        reference_frame_velocity_components=reference_frame_velocity_components,
        reference_frame_axis_origin_components=reference_frame_axis_origin_components,
        reference_frame_axis_direction_components=reference_frame_axis_direction_components,
        mrf_udf_zmotion_name=mrf_udf_zmotion_name,
        mgrid_enable_transient=mgrid_enable_transient,
        mgrid_motion=mgrid_motion,
        mgrid_relative_to_thread=mgrid_relative_to_thread,
        mgrid_omega=mgrid_omega,
        moving_mesh_velocity_components=moving_mesh_velocity_components,
        moving_mesh_axis_origin_components=moving_mesh_axis_origin_components,
        mgrid_udf_zmotion_name=mgrid_udf_zmotion_name,
        solid_motion=solid_motion,
        solid_relative_to_thread=solid_relative_to_thread,
        solid_omega=solid_omega,
        solid_motion_velocity_components=solid_motion_velocity_components,
        solid_motion_axis_origin_components=solid_motion_axis_origin_components,
        solid_motion_axis_direction_components=solid_motion_axis_direction_components,
        solid_udf_zmotion_name=solid_udf_zmotion_name,
        radiating=radiating,
        les_embedded=les_embedded,
        contact_property=contact_property,
        vapor_phase_realgas=vapor_phase_realgas,
        laminar=laminar,
        laminar_mut_zero=laminar_mut_zero,
        les_embedded_spec=les_embedded_spec,
        les_embedded_mom_scheme=les_embedded_mom_scheme,
        les_embedded_c_wale=les_embedded_c_wale,
        les_embedded_c_smag=les_embedded_c_smag,
        glass=glass,
        porous=porous,
        conical=conical,
        dir_spec_cond=dir_spec_cond,
        cursys=cursys,
        cursys_name=cursys_name,
        direction_1_x=direction_1_x,
        direction_1_y=direction_1_y,
        direction_1_z=direction_1_z,
        direction_2_x=direction_2_x,
        direction_2_y=direction_2_y,
        direction_2_z=direction_2_z,
        cone_axis_x=cone_axis_x,
        cone_axis_y=cone_axis_y,
        cone_axis_z=cone_axis_z,
        cone_axis_pt_x=cone_axis_pt_x,
        cone_axis_pt_y=cone_axis_pt_y,
        cone_axis_pt_z=cone_axis_pt_z,
        cone_angle=cone_angle,
        rel_vel_resistance=rel_vel_resistance,
        porous_r_1=porous_r_1,
        porous_r_2=porous_r_2,
        porous_r_3=porous_r_3,
        alt_inertial_form=alt_inertial_form,
        porous_c_1=porous_c_1,
        porous_c_2=porous_c_2,
        porous_c_3=porous_c_3,
        c0=c0,
        c1=c1,
        porosity=porosity,
        viscosity_ratio=viscosity_ratio,
        none=none,
        corey=corey,
        stone_1=stone_1,
        stone_2=stone_2,
        rel_perm_limit_p1=rel_perm_limit_p1,
        rel_perm_limit_p2=rel_perm_limit_p2,
        ref_perm_p1=ref_perm_p1,
        exp_p1=exp_p1,
        res_sat_p1=res_sat_p1,
        ref_perm_p2=ref_perm_p2,
        exp_p2=exp_p2,
        res_sat_p2=res_sat_p2,
        ref_perm_p3=ref_perm_p3,
        exp_p3=exp_p3,
        res_sat_p3=res_sat_p3,
        capillary_pressure=capillary_pressure,
        max_capillary_pressure=max_capillary_pressure,
        van_genuchten_pg=van_genuchten_pg,
        van_genuchten_ng=van_genuchten_ng,
        skjaeveland_nw_pc_coef=skjaeveland_nw_pc_coef,
        skjaeveland_nw_pc_pwr=skjaeveland_nw_pc_pwr,
        skjaeveland_wet_pc_coef=skjaeveland_wet_pc_coef,
        skjaeveland_wet_pc_pwr=skjaeveland_wet_pc_pwr,
        brooks_corey_pe=brooks_corey_pe,
        brooks_corey_ng=brooks_corey_ng,
        leverett_con_ang=leverett_con_ang,
        rp_cbox_p1=rp_cbox_p1,
        rp_edit_p1=rp_edit_p1,
        rel_perm_tabular_p1=rel_perm_tabular_p1,
        rel_perm_table_p1=rel_perm_table_p1,
        rel_perm_satw_p1=rel_perm_satw_p1,
        rel_perm_rp_p1=rel_perm_rp_p1,
        rp_cbox_p2=rp_cbox_p2,
        rp_edit_p2=rp_edit_p2,
        rel_perm_tabular_p2=rel_perm_tabular_p2,
        rel_perm_table_p2=rel_perm_table_p2,
        rel_perm_satw_p2=rel_perm_satw_p2,
        rel_perm_rp_p2=rel_perm_rp_p2,
        wetting_phase=wetting_phase,
        non_wetting_phase=non_wetting_phase,
        equib_thermal=equib_thermal,
        non_equib_thermal=non_equib_thermal,
        solid_material=solid_material,
        area_density=area_density,
        heat_transfer_coeff=heat_transfer_coeff,
        fanzone=fanzone,
        fan_zone_list=fan_zone_list,
        fan_thickness=fan_thickness,
        fan_hub_rad=fan_hub_rad,
        fan_tip_rad=fan_tip_rad,
        fan_x_origin=fan_x_origin,
        fan_y_origin=fan_y_origin,
        fan_z_origin=fan_z_origin,
        fan_rot_dir=fan_rot_dir,
        fan_opert_angvel=fan_opert_angvel,
        fan_inflection_point=fan_inflection_point,
        limit_flow_fan=limit_flow_fan,
        max_flow_rate=max_flow_rate,
        min_flow_rate=min_flow_rate,
        tan_source_term=tan_source_term,
        rad_source_term=rad_source_term,
        axial_source_term=axial_source_term,
        fan_axial_source_method=fan_axial_source_method,
        fan_pre_jump=fan_pre_jump,
        fan_curve_fit=fan_curve_fit,
        fan_poly_order=fan_poly_order,
        fan_ini_flow=fan_ini_flow,
        fan_test_angvel=fan_test_angvel,
        fan_test_temp=fan_test_temp,
        read_fan_curve=read_fan_curve,
        reaction_mechs=reaction_mechs_1,
        react=react,
        surface_volume_ratio=surface_volume_ratio,
        electrolyte=electrolyte,
        mp_compressive_beta_max=mp_compressive_beta_max,
        mp_boiling_zone=mp_boiling_zone,
        numerical_beach=numerical_beach,
        beach_id=beach_id,
        beach_multi_dir=beach_multi_dir,
        beach_damp_type=beach_damp_type,
        beach_inlet_bndr=beach_inlet_bndr,
        beach_fs_level=beach_fs_level,
        beach_bottom_level=beach_bottom_level,
        beach_dir_ni=beach_dir_ni,
        beach_dir_nj=beach_dir_nj,
        beach_dir_nk=beach_dir_nk,
        beach_damp_len_spec=beach_damp_len_spec,
        beach_wave_len=beach_wave_len,
        beach_len_factor=beach_len_factor,
        beach_start_point=beach_start_point,
        beach_end_point=beach_end_point,
        beach_dir_list=beach_dir_list,
        beach_damp_relative=beach_damp_relative,
        beach_damp_resist_lin=beach_damp_resist_lin,
        beach_damp_resist=beach_damp_resist,
        porous_structure=porous_structure,
        structure_material=structure_material,
        anisotropic_spe_diff=anisotropic_spe_diff,
        spe_diff_xx=spe_diff_xx,
        spe_diff_xy=spe_diff_xy,
        spe_diff_xz=spe_diff_xz,
        spe_diff_yx=spe_diff_yx,
        spe_diff_yy=spe_diff_yy,
        spe_diff_yz=spe_diff_yz,
        spe_diff_zx=spe_diff_zx,
        spe_diff_zy=spe_diff_zy,
        spe_diff_zz=spe_diff_zz,
    )
    return_type = 'object'

class fluid_1(NamedObject[fluid_1_child], CreatableNamedObjectMixinOld[fluid_1_child]):
    """
    'fluid' child.
    """
    _version = '222'
    fluent_name = 'fluid'
    _python_name = 'fluid'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = fluid_1_child
    return_type = 'object'

class pcb_model(Boolean, AllowedValuesMixin):
    """
    'pcb_model' child.
    """
    _version = '222'
    fluent_name = 'pcb-model'
    _python_name = 'pcb_model'
    return_type = 'object'

class ecad_name(String, AllowedValuesMixin):
    """
    'ecad_name' child.
    """
    _version = '222'
    fluent_name = 'ecad-name'
    _python_name = 'ecad_name'
    return_type = 'object'

class choice(String, AllowedValuesMixin):
    """
    'choice' child.
    """
    _version = '222'
    fluent_name = 'choice'
    _python_name = 'choice'
    return_type = 'object'

class rows(Real, AllowedValuesMixin):
    """
    'rows' child.
    """
    _version = '222'
    fluent_name = 'rows'
    _python_name = 'rows'
    return_type = 'object'

class columns(Real, AllowedValuesMixin):
    """
    'columns' child.
    """
    _version = '222'
    fluent_name = 'columns'
    _python_name = 'columns'
    return_type = 'object'

class ref_frame(String, AllowedValuesMixin):
    """
    'ref_frame' child.
    """
    _version = '222'
    fluent_name = 'ref-frame'
    _python_name = 'ref_frame'
    return_type = 'object'

class pwr_names(StringList, AllowedValuesMixin):
    """
    'pwr_names' child.
    """
    _version = '222'
    fluent_name = 'pwr-names'
    _python_name = 'pwr_names'
    return_type = 'object'

class pcb_zone_info(Group):
    """
    'pcb_zone_info' child.
    """
    _version = '222'
    fluent_name = 'pcb-zone-info'
    _python_name = 'pcb_zone_info'
    child_names = ['ecad_name', 'choice', 'rows', 'columns', 'ref_frame', 'pwr_names']
    _child_classes = dict(
        ecad_name=ecad_name,
        choice=choice,
        rows=rows,
        columns=columns,
        ref_frame=ref_frame,
        pwr_names=pwr_names,
    )
    return_type = 'object'

class phase_1_child(Group):
    """
    'child_object_type' of phase.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'phase_child'
    child_names = ['material', 'sources', 'source_terms', 'fixed', 'cylindrical_fixed_var', 'fixes', 'motion_spec', 'relative_to_thread', 'omega', 'axis_origin_component', 'axis_direction_component', 'udf_zmotion_name', 'mrf_motion', 'mrf_relative_to_thread', 'mrf_omega', 'reference_frame_velocity_components', 'reference_frame_axis_origin_components', 'reference_frame_axis_direction_components', 'mrf_udf_zmotion_name', 'mgrid_enable_transient', 'mgrid_motion', 'mgrid_relative_to_thread', 'mgrid_omega', 'moving_mesh_velocity_components', 'moving_mesh_axis_origin_components', 'mgrid_udf_zmotion_name', 'solid_motion', 'solid_relative_to_thread', 'solid_omega', 'solid_motion_velocity_components', 'solid_motion_axis_origin_components', 'solid_motion_axis_direction_components', 'solid_udf_zmotion_name', 'radiating', 'les_embedded', 'contact_property', 'vapor_phase_realgas', 'cursys', 'cursys_name', 'pcb_model', 'pcb_zone_info']
    _child_classes = dict(
        material=material,
        sources=sources,
        source_terms=source_terms,
        fixed=fixed,
        cylindrical_fixed_var=cylindrical_fixed_var,
        fixes=fixes,
        motion_spec=motion_spec,
        relative_to_thread=relative_to_thread,
        omega=omega,
        axis_origin_component=axis_origin_component,
        axis_direction_component=axis_direction_component,
        udf_zmotion_name=udf_zmotion_name,
        mrf_motion=mrf_motion,
        mrf_relative_to_thread=mrf_relative_to_thread,
        mrf_omega=mrf_omega,
        reference_frame_velocity_components=reference_frame_velocity_components,
        reference_frame_axis_origin_components=reference_frame_axis_origin_components,
        reference_frame_axis_direction_components=reference_frame_axis_direction_components,
        mrf_udf_zmotion_name=mrf_udf_zmotion_name,
        mgrid_enable_transient=mgrid_enable_transient,
        mgrid_motion=mgrid_motion,
        mgrid_relative_to_thread=mgrid_relative_to_thread,
        mgrid_omega=mgrid_omega,
        moving_mesh_velocity_components=moving_mesh_velocity_components,
        moving_mesh_axis_origin_components=moving_mesh_axis_origin_components,
        mgrid_udf_zmotion_name=mgrid_udf_zmotion_name,
        solid_motion=solid_motion,
        solid_relative_to_thread=solid_relative_to_thread,
        solid_omega=solid_omega,
        solid_motion_velocity_components=solid_motion_velocity_components,
        solid_motion_axis_origin_components=solid_motion_axis_origin_components,
        solid_motion_axis_direction_components=solid_motion_axis_direction_components,
        solid_udf_zmotion_name=solid_udf_zmotion_name,
        radiating=radiating,
        les_embedded=les_embedded,
        contact_property=contact_property,
        vapor_phase_realgas=vapor_phase_realgas,
        cursys=cursys,
        cursys_name=cursys_name,
        pcb_model=pcb_model,
        pcb_zone_info=pcb_zone_info,
    )
    return_type = 'object'

class phase_1(NamedObject[phase_1_child], CreatableNamedObjectMixinOld[phase_1_child]):
    """
    'phase' child.
    """
    _version = '222'
    fluent_name = 'phase'
    _python_name = 'phase'
    child_object_type = phase_1_child
    return_type = 'object'

class solid_1_child(Group):
    """
    'child_object_type' of solid.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'solid_child'
    child_names = ['phase', 'material', 'sources', 'source_terms', 'fixed', 'cylindrical_fixed_var', 'fixes', 'motion_spec', 'relative_to_thread', 'omega', 'axis_origin_component', 'axis_direction_component', 'udf_zmotion_name', 'mrf_motion', 'mrf_relative_to_thread', 'mrf_omega', 'reference_frame_velocity_components', 'reference_frame_axis_origin_components', 'reference_frame_axis_direction_components', 'mrf_udf_zmotion_name', 'mgrid_enable_transient', 'mgrid_motion', 'mgrid_relative_to_thread', 'mgrid_omega', 'moving_mesh_velocity_components', 'moving_mesh_axis_origin_components', 'mgrid_udf_zmotion_name', 'solid_motion', 'solid_relative_to_thread', 'solid_omega', 'solid_motion_velocity_components', 'solid_motion_axis_origin_components', 'solid_motion_axis_direction_components', 'solid_udf_zmotion_name', 'radiating', 'les_embedded', 'contact_property', 'vapor_phase_realgas', 'cursys', 'cursys_name', 'pcb_model', 'pcb_zone_info']
    _child_classes = dict(
        phase=phase_1,
        material=material,
        sources=sources,
        source_terms=source_terms,
        fixed=fixed,
        cylindrical_fixed_var=cylindrical_fixed_var,
        fixes=fixes,
        motion_spec=motion_spec,
        relative_to_thread=relative_to_thread,
        omega=omega,
        axis_origin_component=axis_origin_component,
        axis_direction_component=axis_direction_component,
        udf_zmotion_name=udf_zmotion_name,
        mrf_motion=mrf_motion,
        mrf_relative_to_thread=mrf_relative_to_thread,
        mrf_omega=mrf_omega,
        reference_frame_velocity_components=reference_frame_velocity_components,
        reference_frame_axis_origin_components=reference_frame_axis_origin_components,
        reference_frame_axis_direction_components=reference_frame_axis_direction_components,
        mrf_udf_zmotion_name=mrf_udf_zmotion_name,
        mgrid_enable_transient=mgrid_enable_transient,
        mgrid_motion=mgrid_motion,
        mgrid_relative_to_thread=mgrid_relative_to_thread,
        mgrid_omega=mgrid_omega,
        moving_mesh_velocity_components=moving_mesh_velocity_components,
        moving_mesh_axis_origin_components=moving_mesh_axis_origin_components,
        mgrid_udf_zmotion_name=mgrid_udf_zmotion_name,
        solid_motion=solid_motion,
        solid_relative_to_thread=solid_relative_to_thread,
        solid_omega=solid_omega,
        solid_motion_velocity_components=solid_motion_velocity_components,
        solid_motion_axis_origin_components=solid_motion_axis_origin_components,
        solid_motion_axis_direction_components=solid_motion_axis_direction_components,
        solid_udf_zmotion_name=solid_udf_zmotion_name,
        radiating=radiating,
        les_embedded=les_embedded,
        contact_property=contact_property,
        vapor_phase_realgas=vapor_phase_realgas,
        cursys=cursys,
        cursys_name=cursys_name,
        pcb_model=pcb_model,
        pcb_zone_info=pcb_zone_info,
    )
    return_type = 'object'

class solid_1(NamedObject[solid_1_child], CreatableNamedObjectMixinOld[solid_1_child]):
    """
    'solid' child.
    """
    _version = '222'
    fluent_name = 'solid'
    _python_name = 'solid'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = solid_1_child
    return_type = 'object'

class cell_zone_conditions(Group):
    """
    'cell_zone_conditions' child.
    """
    _version = '222'
    fluent_name = 'cell-zone-conditions'
    _python_name = 'cell_zone_conditions'
    child_names = ['fluid', 'solid']
    _child_classes = dict(
        fluid=fluid_1,
        solid=solid_1,
    )
    return_type = 'object'

class geom_disable(Boolean, AllowedValuesMixin):
    """
    'geom_disable' child.
    """
    _version = '222'
    fluent_name = 'geom-disable?'
    _python_name = 'geom_disable'
    return_type = 'object'

class geom_dir_spec(Boolean, AllowedValuesMixin):
    """
    'geom_dir_spec' child.
    """
    _version = '222'
    fluent_name = 'geom-dir-spec'
    _python_name = 'geom_dir_spec'
    return_type = 'object'

class geom_dir_x(Real, AllowedValuesMixin):
    """
    'geom_dir_x' child.
    """
    _version = '222'
    fluent_name = 'geom-dir-x'
    _python_name = 'geom_dir_x'
    return_type = 'object'

class geom_dir_y(Real, AllowedValuesMixin):
    """
    'geom_dir_y' child.
    """
    _version = '222'
    fluent_name = 'geom-dir-y'
    _python_name = 'geom_dir_y'
    return_type = 'object'

class geom_dir_z(Real, AllowedValuesMixin):
    """
    'geom_dir_z' child.
    """
    _version = '222'
    fluent_name = 'geom-dir-z'
    _python_name = 'geom_dir_z'
    return_type = 'object'

class geom_levels(Integer, AllowedValuesMixin):
    """
    'geom_levels' child.
    """
    _version = '222'
    fluent_name = 'geom-levels'
    _python_name = 'geom_levels'
    return_type = 'object'

class geom_bgthread(Integer, AllowedValuesMixin):
    """
    'geom_bgthread' child.
    """
    _version = '222'
    fluent_name = 'geom-bgthread'
    _python_name = 'geom_bgthread'
    return_type = 'object'

class phase_2_child(Group):
    """
    'child_object_type' of phase.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'phase_child'
    child_names = ['geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread']
    _child_classes = dict(
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
    )
    return_type = 'object'

class phase_2(NamedObject[phase_2_child], CreatableNamedObjectMixinOld[phase_2_child]):
    """
    'phase' child.
    """
    _version = '222'
    fluent_name = 'phase'
    _python_name = 'phase'
    child_object_type = phase_2_child
    return_type = 'object'

class axis_child(Group):
    """
    'child_object_type' of axis.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'axis_child'
    child_names = ['phase', 'geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread']
    _child_classes = dict(
        phase=phase_2,
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
    )
    return_type = 'object'

class axis(NamedObject[axis_child], CreatableNamedObjectMixinOld[axis_child]):
    """
    'axis' child.
    """
    _version = '222'
    fluent_name = 'axis'
    _python_name = 'axis'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = axis_child
    return_type = 'object'

class degassing_child(Group):
    """
    'child_object_type' of degassing.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'degassing_child'
    child_names = ['phase', 'geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread']
    _child_classes = dict(
        phase=phase_2,
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
    )
    return_type = 'object'

class degassing(NamedObject[degassing_child], CreatableNamedObjectMixinOld[degassing_child]):
    """
    'degassing' child.
    """
    _version = '222'
    fluent_name = 'degassing'
    _python_name = 'degassing'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = degassing_child
    return_type = 'object'

class open_channel(Boolean, AllowedValuesMixin):
    """
    'open_channel' child.
    """
    _version = '222'
    fluent_name = 'open-channel?'
    _python_name = 'open_channel'
    return_type = 'object'

class outlet_number(Integer, AllowedValuesMixin):
    """
    'outlet_number' child.
    """
    _version = '222'
    fluent_name = 'outlet-number'
    _python_name = 'outlet_number'
    return_type = 'object'

class pressure_spec_method(String, AllowedValuesMixin):
    """
    'pressure_spec_method' child.
    """
    _version = '222'
    fluent_name = 'pressure-spec-method'
    _python_name = 'pressure_spec_method'
    return_type = 'object'

class press_spec(String, AllowedValuesMixin):
    """
    'press_spec' child.
    """
    _version = '222'
    fluent_name = 'press-spec'
    _python_name = 'press_spec'
    return_type = 'object'

class frame_of_reference(String, AllowedValuesMixin):
    """
    'frame_of_reference' child.
    """
    _version = '222'
    fluent_name = 'frame-of-reference'
    _python_name = 'frame_of_reference'
    return_type = 'object'

class phase_spec(String, AllowedValuesMixin):
    """
    'phase_spec' child.
    """
    _version = '222'
    fluent_name = 'phase-spec'
    _python_name = 'phase_spec'
    return_type = 'object'

class ht_local(Group):
    """
    'ht_local' child.
    """
    _version = '222'
    fluent_name = 'ht-local'
    _python_name = 'ht_local'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class p(Group):
    """
    'p' child.
    """
    _version = '222'
    fluent_name = 'p'
    _python_name = 'p'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class p_profile_multiplier(Real, AllowedValuesMixin):
    """
    'p_profile_multiplier' child.
    """
    _version = '222'
    fluent_name = 'p-profile-multiplier'
    _python_name = 'p_profile_multiplier'
    return_type = 'object'

class ht_bottom(Group):
    """
    'ht_bottom' child.
    """
    _version = '222'
    fluent_name = 'ht-bottom'
    _python_name = 'ht_bottom'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class den_spec(String, AllowedValuesMixin):
    """
    'den_spec' child.
    """
    _version = '222'
    fluent_name = 'den-spec'
    _python_name = 'den_spec'
    return_type = 'object'

class t0(Group):
    """
    't0' child.
    """
    _version = '222'
    fluent_name = 't0'
    _python_name = 't0'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class direction_spec(String, AllowedValuesMixin):
    """
    'direction_spec' child.
    """
    _version = '222'
    fluent_name = 'direction-spec'
    _python_name = 'direction_spec'
    return_type = 'object'

class coordinate_system(String, AllowedValuesMixin):
    """
    'coordinate_system' child.
    """
    _version = '222'
    fluent_name = 'coordinate-system'
    _python_name = 'coordinate_system'
    return_type = 'object'

class flow_direction_component_child(Group):
    """
    'child_object_type' of flow_direction_component.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'flow_direction_component_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class flow_direction_component(ListObject[flow_direction_component_child]):
    """
    'flow_direction_component' child.
    """
    _version = '222'
    fluent_name = 'flow-direction-component'
    _python_name = 'flow_direction_component'
    child_object_type = flow_direction_component_child
    return_type = 'object'

class axis_direction_component_1_child(Real, AllowedValuesMixin):
    """
    'child_object_type' of axis_direction_component.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'axis_direction_component_child'
    return_type = 'object'

class axis_direction_component_1(ListObject[axis_direction_component_1_child]):
    """
    'axis_direction_component' child.
    """
    _version = '222'
    fluent_name = 'axis-direction-component'
    _python_name = 'axis_direction_component'
    child_object_type = axis_direction_component_1_child
    return_type = 'object'

class axis_origin_component_1_child(Real, AllowedValuesMixin):
    """
    'child_object_type' of axis_origin_component.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'axis_origin_component_child'
    return_type = 'object'

class axis_origin_component_1(ListObject[axis_origin_component_1_child]):
    """
    'axis_origin_component' child.
    """
    _version = '222'
    fluent_name = 'axis-origin-component'
    _python_name = 'axis_origin_component'
    child_object_type = axis_origin_component_1_child
    return_type = 'object'

class ke_spec(String, AllowedValuesMixin):
    """
    'ke_spec' child.
    """
    _version = '222'
    fluent_name = 'ke-spec'
    _python_name = 'ke_spec'
    return_type = 'object'

class nut(Group):
    """
    'nut' child.
    """
    _version = '222'
    fluent_name = 'nut'
    _python_name = 'nut'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class kl(Group):
    """
    'kl' child.
    """
    _version = '222'
    fluent_name = 'kl'
    _python_name = 'kl'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class intermit(Group):
    """
    'intermit' child.
    """
    _version = '222'
    fluent_name = 'intermit'
    _python_name = 'intermit'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class k(Group):
    """
    'k' child.
    """
    _version = '222'
    fluent_name = 'k'
    _python_name = 'k'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class e(Group):
    """
    'e' child.
    """
    _version = '222'
    fluent_name = 'e'
    _python_name = 'e'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class o(Group):
    """
    'o' child.
    """
    _version = '222'
    fluent_name = 'o'
    _python_name = 'o'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class v2(Group):
    """
    'v2' child.
    """
    _version = '222'
    fluent_name = 'v2'
    _python_name = 'v2'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class turb_intensity(Real, AllowedValuesMixin):
    """
    'turb_intensity' child.
    """
    _version = '222'
    fluent_name = 'turb-intensity'
    _python_name = 'turb_intensity'
    return_type = 'object'

class turb_length_scale(Real, AllowedValuesMixin):
    """
    'turb_length_scale' child.
    """
    _version = '222'
    fluent_name = 'turb-length-scale'
    _python_name = 'turb_length_scale'
    return_type = 'object'

class turb_hydraulic_diam(Real, AllowedValuesMixin):
    """
    'turb_hydraulic_diam' child.
    """
    _version = '222'
    fluent_name = 'turb-hydraulic-diam'
    _python_name = 'turb_hydraulic_diam'
    return_type = 'object'

class turb_viscosity_ratio(Real, AllowedValuesMixin):
    """
    'turb_viscosity_ratio' child.
    """
    _version = '222'
    fluent_name = 'turb-viscosity-ratio'
    _python_name = 'turb_viscosity_ratio'
    return_type = 'object'

class turb_viscosity_ratio_profile(Group):
    """
    'turb_viscosity_ratio_profile' child.
    """
    _version = '222'
    fluent_name = 'turb-viscosity-ratio-profile'
    _python_name = 'turb_viscosity_ratio_profile'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class rst_spec(String, AllowedValuesMixin):
    """
    'rst_spec' child.
    """
    _version = '222'
    fluent_name = 'rst-spec'
    _python_name = 'rst_spec'
    return_type = 'object'

class uu(Group):
    """
    'uu' child.
    """
    _version = '222'
    fluent_name = 'uu'
    _python_name = 'uu'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class vv(Group):
    """
    'vv' child.
    """
    _version = '222'
    fluent_name = 'vv'
    _python_name = 'vv'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class ww(Group):
    """
    'ww' child.
    """
    _version = '222'
    fluent_name = 'ww'
    _python_name = 'ww'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class uv(Group):
    """
    'uv' child.
    """
    _version = '222'
    fluent_name = 'uv'
    _python_name = 'uv'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class vw(Group):
    """
    'vw' child.
    """
    _version = '222'
    fluent_name = 'vw'
    _python_name = 'vw'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class uw(Group):
    """
    'uw' child.
    """
    _version = '222'
    fluent_name = 'uw'
    _python_name = 'uw'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class ksgs_spec(String, AllowedValuesMixin):
    """
    'ksgs_spec' child.
    """
    _version = '222'
    fluent_name = 'ksgs-spec'
    _python_name = 'ksgs_spec'
    return_type = 'object'

class ksgs(Group):
    """
    'ksgs' child.
    """
    _version = '222'
    fluent_name = 'ksgs'
    _python_name = 'ksgs'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class sgs_turb_intensity(Real, AllowedValuesMixin):
    """
    'sgs_turb_intensity' child.
    """
    _version = '222'
    fluent_name = 'sgs-turb-intensity'
    _python_name = 'sgs_turb_intensity'
    return_type = 'object'

class radiation_bc(String, AllowedValuesMixin):
    """
    'radiation_bc' child.
    """
    _version = '222'
    fluent_name = 'radiation-bc'
    _python_name = 'radiation_bc'
    return_type = 'object'

class radial_direction_component_child(Group):
    """
    'child_object_type' of radial_direction_component.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'radial_direction_component_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class radial_direction_component(ListObject[radial_direction_component_child]):
    """
    'radial_direction_component' child.
    """
    _version = '222'
    fluent_name = 'radial-direction-component'
    _python_name = 'radial_direction_component'
    child_object_type = radial_direction_component_child
    return_type = 'object'

class coll_dtheta(Real, AllowedValuesMixin):
    """
    'coll_dtheta' child.
    """
    _version = '222'
    fluent_name = 'coll-dtheta'
    _python_name = 'coll_dtheta'
    return_type = 'object'

class coll_dphi(Real, AllowedValuesMixin):
    """
    'coll_dphi' child.
    """
    _version = '222'
    fluent_name = 'coll-dphi'
    _python_name = 'coll_dphi'
    return_type = 'object'

class band_q_irrad_child(Group):
    """
    'child_object_type' of band_q_irrad.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'band_q_irrad_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class band_q_irrad(NamedObject[band_q_irrad_child], CreatableNamedObjectMixinOld[band_q_irrad_child]):
    """
    'band_q_irrad' child.
    """
    _version = '222'
    fluent_name = 'band-q-irrad'
    _python_name = 'band_q_irrad'
    child_object_type = band_q_irrad_child
    return_type = 'object'

class band_q_irrad_diffuse_child(Group):
    """
    'child_object_type' of band_q_irrad_diffuse.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'band_q_irrad_diffuse_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class band_q_irrad_diffuse(NamedObject[band_q_irrad_diffuse_child], CreatableNamedObjectMixinOld[band_q_irrad_diffuse_child]):
    """
    'band_q_irrad_diffuse' child.
    """
    _version = '222'
    fluent_name = 'band-q-irrad-diffuse'
    _python_name = 'band_q_irrad_diffuse'
    child_object_type = band_q_irrad_diffuse_child
    return_type = 'object'

class parallel_collimated_beam(Boolean, AllowedValuesMixin):
    """
    'parallel_collimated_beam' child.
    """
    _version = '222'
    fluent_name = 'parallel-collimated-beam?'
    _python_name = 'parallel_collimated_beam'
    return_type = 'object'

class solar_direction(Boolean, AllowedValuesMixin):
    """
    'solar_direction' child.
    """
    _version = '222'
    fluent_name = 'solar-direction?'
    _python_name = 'solar_direction'
    return_type = 'object'

class solar_irradiation(Boolean, AllowedValuesMixin):
    """
    'solar_irradiation' child.
    """
    _version = '222'
    fluent_name = 'solar-irradiation?'
    _python_name = 'solar_irradiation'
    return_type = 'object'

class t_b_b_spec(String, AllowedValuesMixin):
    """
    't_b_b_spec' child.
    """
    _version = '222'
    fluent_name = 't-b-b-spec'
    _python_name = 't_b_b_spec'
    return_type = 'object'

class t_b_b(Real, AllowedValuesMixin):
    """
    't_b_b' child.
    """
    _version = '222'
    fluent_name = 't-b-b'
    _python_name = 't_b_b'
    return_type = 'object'

class in_emiss(Group):
    """
    'in_emiss' child.
    """
    _version = '222'
    fluent_name = 'in-emiss'
    _python_name = 'in_emiss'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class fmean(Group):
    """
    'fmean' child.
    """
    _version = '222'
    fluent_name = 'fmean'
    _python_name = 'fmean'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class fmean2(Group):
    """
    'fmean2' child.
    """
    _version = '222'
    fluent_name = 'fmean2'
    _python_name = 'fmean2'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class fvar(Group):
    """
    'fvar' child.
    """
    _version = '222'
    fluent_name = 'fvar'
    _python_name = 'fvar'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class fvar2(Group):
    """
    'fvar2' child.
    """
    _version = '222'
    fluent_name = 'fvar2'
    _python_name = 'fvar2'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class granular_temperature(Group):
    """
    'granular_temperature' child.
    """
    _version = '222'
    fluent_name = 'granular-temperature'
    _python_name = 'granular_temperature'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class iac(Group):
    """
    'iac' child.
    """
    _version = '222'
    fluent_name = 'iac'
    _python_name = 'iac'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class lsfun(Group):
    """
    'lsfun' child.
    """
    _version = '222'
    fluent_name = 'lsfun'
    _python_name = 'lsfun'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class vof_spec(String, AllowedValuesMixin):
    """
    'vof_spec' child.
    """
    _version = '222'
    fluent_name = 'vof-spec'
    _python_name = 'vof_spec'
    return_type = 'object'

class volume_fraction(Group):
    """
    'volume_fraction' child.
    """
    _version = '222'
    fluent_name = 'volume-fraction'
    _python_name = 'volume_fraction'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class species_in_mole_fractions(Boolean, AllowedValuesMixin):
    """
    'species_in_mole_fractions' child.
    """
    _version = '222'
    fluent_name = 'species-in-mole-fractions?'
    _python_name = 'species_in_mole_fractions'
    return_type = 'object'

class mf_child(Group):
    """
    'child_object_type' of mf.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'mf_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class mf(NamedObject[mf_child], CreatableNamedObjectMixinOld[mf_child]):
    """
    'mf' child.
    """
    _version = '222'
    fluent_name = 'mf'
    _python_name = 'mf'
    child_object_type = mf_child
    return_type = 'object'

class elec_potential_type(String, AllowedValuesMixin):
    """
    'elec_potential_type' child.
    """
    _version = '222'
    fluent_name = 'elec-potential-type'
    _python_name = 'elec_potential_type'
    return_type = 'object'

class potential_value(Group):
    """
    'potential_value' child.
    """
    _version = '222'
    fluent_name = 'potential-value'
    _python_name = 'potential_value'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class dual_potential_type(String, AllowedValuesMixin):
    """
    'dual_potential_type' child.
    """
    _version = '222'
    fluent_name = 'dual-potential-type'
    _python_name = 'dual_potential_type'
    return_type = 'object'

class dual_potential_value(Group):
    """
    'dual_potential_value' child.
    """
    _version = '222'
    fluent_name = 'dual-potential-value'
    _python_name = 'dual_potential_value'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class x_displacement_type(String, AllowedValuesMixin):
    """
    'x_displacement_type' child.
    """
    _version = '222'
    fluent_name = 'x-displacement-type'
    _python_name = 'x_displacement_type'
    return_type = 'object'

class x_displacement_value(Group):
    """
    'x_displacement_value' child.
    """
    _version = '222'
    fluent_name = 'x-displacement-value'
    _python_name = 'x_displacement_value'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class y_displacement_type(String, AllowedValuesMixin):
    """
    'y_displacement_type' child.
    """
    _version = '222'
    fluent_name = 'y-displacement-type'
    _python_name = 'y_displacement_type'
    return_type = 'object'

class y_displacement_value(Group):
    """
    'y_displacement_value' child.
    """
    _version = '222'
    fluent_name = 'y-displacement-value'
    _python_name = 'y_displacement_value'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class z_displacement_type(String, AllowedValuesMixin):
    """
    'z_displacement_type' child.
    """
    _version = '222'
    fluent_name = 'z-displacement-type'
    _python_name = 'z_displacement_type'
    return_type = 'object'

class z_displacement_value(Group):
    """
    'z_displacement_value' child.
    """
    _version = '222'
    fluent_name = 'z-displacement-value'
    _python_name = 'z_displacement_value'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class prob_mode_1(Group):
    """
    'prob_mode_1' child.
    """
    _version = '222'
    fluent_name = 'prob-mode-1'
    _python_name = 'prob_mode_1'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class prob_mode_2(Group):
    """
    'prob_mode_2' child.
    """
    _version = '222'
    fluent_name = 'prob-mode-2'
    _python_name = 'prob_mode_2'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class prob_mode_3(Group):
    """
    'prob_mode_3' child.
    """
    _version = '222'
    fluent_name = 'prob-mode-3'
    _python_name = 'prob_mode_3'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class premixc(Group):
    """
    'premixc' child.
    """
    _version = '222'
    fluent_name = 'premixc'
    _python_name = 'premixc'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class premixc_var(Group):
    """
    'premixc_var' child.
    """
    _version = '222'
    fluent_name = 'premixc-var'
    _python_name = 'premixc_var'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class ecfm_sigma(Group):
    """
    'ecfm_sigma' child.
    """
    _version = '222'
    fluent_name = 'ecfm-sigma'
    _python_name = 'ecfm_sigma'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class inert(Group):
    """
    'inert' child.
    """
    _version = '222'
    fluent_name = 'inert'
    _python_name = 'inert'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pollut_no(Group):
    """
    'pollut_no' child.
    """
    _version = '222'
    fluent_name = 'pollut-no'
    _python_name = 'pollut_no'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pollut_hcn(Group):
    """
    'pollut_hcn' child.
    """
    _version = '222'
    fluent_name = 'pollut-hcn'
    _python_name = 'pollut_hcn'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pollut_nh3(Group):
    """
    'pollut_nh3' child.
    """
    _version = '222'
    fluent_name = 'pollut-nh3'
    _python_name = 'pollut_nh3'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pollut_n2o(Group):
    """
    'pollut_n2o' child.
    """
    _version = '222'
    fluent_name = 'pollut-n2o'
    _python_name = 'pollut_n2o'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pollut_urea(Group):
    """
    'pollut_urea' child.
    """
    _version = '222'
    fluent_name = 'pollut-urea'
    _python_name = 'pollut_urea'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pollut_hnco(Group):
    """
    'pollut_hnco' child.
    """
    _version = '222'
    fluent_name = 'pollut-hnco'
    _python_name = 'pollut_hnco'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pollut_nco(Group):
    """
    'pollut_nco' child.
    """
    _version = '222'
    fluent_name = 'pollut-nco'
    _python_name = 'pollut_nco'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pollut_so2(Group):
    """
    'pollut_so2' child.
    """
    _version = '222'
    fluent_name = 'pollut-so2'
    _python_name = 'pollut_so2'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pollut_h2s(Group):
    """
    'pollut_h2s' child.
    """
    _version = '222'
    fluent_name = 'pollut-h2s'
    _python_name = 'pollut_h2s'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pollut_so3(Group):
    """
    'pollut_so3' child.
    """
    _version = '222'
    fluent_name = 'pollut-so3'
    _python_name = 'pollut_so3'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pollut_sh(Group):
    """
    'pollut_sh' child.
    """
    _version = '222'
    fluent_name = 'pollut-sh'
    _python_name = 'pollut_sh'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pollut_so(Group):
    """
    'pollut_so' child.
    """
    _version = '222'
    fluent_name = 'pollut-so'
    _python_name = 'pollut_so'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pollut_soot(Group):
    """
    'pollut_soot' child.
    """
    _version = '222'
    fluent_name = 'pollut-soot'
    _python_name = 'pollut_soot'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pollut_nuclei(Group):
    """
    'pollut_nuclei' child.
    """
    _version = '222'
    fluent_name = 'pollut-nuclei'
    _python_name = 'pollut_nuclei'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pollut_ctar(Group):
    """
    'pollut_ctar' child.
    """
    _version = '222'
    fluent_name = 'pollut-ctar'
    _python_name = 'pollut_ctar'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pollut_hg(Group):
    """
    'pollut_hg' child.
    """
    _version = '222'
    fluent_name = 'pollut-hg'
    _python_name = 'pollut_hg'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pollut_hgcl2(Group):
    """
    'pollut_hgcl2' child.
    """
    _version = '222'
    fluent_name = 'pollut-hgcl2'
    _python_name = 'pollut_hgcl2'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pollut_hcl(Group):
    """
    'pollut_hcl' child.
    """
    _version = '222'
    fluent_name = 'pollut-hcl'
    _python_name = 'pollut_hcl'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pollut_hgo(Group):
    """
    'pollut_hgo' child.
    """
    _version = '222'
    fluent_name = 'pollut-hgo'
    _python_name = 'pollut_hgo'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pollut_cl(Group):
    """
    'pollut_cl' child.
    """
    _version = '222'
    fluent_name = 'pollut-cl'
    _python_name = 'pollut_cl'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pollut_cl2(Group):
    """
    'pollut_cl2' child.
    """
    _version = '222'
    fluent_name = 'pollut-cl2'
    _python_name = 'pollut_cl2'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pollut_hgcl(Group):
    """
    'pollut_hgcl' child.
    """
    _version = '222'
    fluent_name = 'pollut-hgcl'
    _python_name = 'pollut_hgcl'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pollut_hocl(Group):
    """
    'pollut_hocl' child.
    """
    _version = '222'
    fluent_name = 'pollut-hocl'
    _python_name = 'pollut_hocl'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class tss_scalar_child(Group):
    """
    'child_object_type' of tss_scalar.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'tss_scalar_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class tss_scalar(NamedObject[tss_scalar_child], CreatableNamedObjectMixinOld[tss_scalar_child]):
    """
    'tss_scalar' child.
    """
    _version = '222'
    fluent_name = 'tss-scalar'
    _python_name = 'tss_scalar'
    child_object_type = tss_scalar_child
    return_type = 'object'

class fensapice_flow_bc_subtype(Integer, AllowedValuesMixin):
    """
    'fensapice_flow_bc_subtype' child.
    """
    _version = '222'
    fluent_name = 'fensapice-flow-bc-subtype'
    _python_name = 'fensapice_flow_bc_subtype'
    return_type = 'object'

class uds_bc_child(String, AllowedValuesMixin):
    """
    'child_object_type' of uds_bc.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'uds_bc_child'
    return_type = 'object'

class uds_bc(NamedObject[uds_bc_child], CreatableNamedObjectMixinOld[uds_bc_child]):
    """
    'uds_bc' child.
    """
    _version = '222'
    fluent_name = 'uds-bc'
    _python_name = 'uds_bc'
    child_object_type = uds_bc_child
    return_type = 'object'

class uds_child(Group):
    """
    'child_object_type' of uds.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'uds_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class uds(NamedObject[uds_child], CreatableNamedObjectMixinOld[uds_child]):
    """
    'uds' child.
    """
    _version = '222'
    fluent_name = 'uds'
    _python_name = 'uds'
    child_object_type = uds_child
    return_type = 'object'

class pb_disc_bc_child(String, AllowedValuesMixin):
    """
    'child_object_type' of pb_disc_bc.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'pb_disc_bc_child'
    return_type = 'object'

class pb_disc_bc(NamedObject[pb_disc_bc_child], CreatableNamedObjectMixinOld[pb_disc_bc_child]):
    """
    'pb_disc_bc' child.
    """
    _version = '222'
    fluent_name = 'pb-disc-bc'
    _python_name = 'pb_disc_bc'
    child_object_type = pb_disc_bc_child
    return_type = 'object'

class pb_disc_child(Group):
    """
    'child_object_type' of pb_disc.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'pb_disc_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pb_disc(NamedObject[pb_disc_child], CreatableNamedObjectMixinOld[pb_disc_child]):
    """
    'pb_disc' child.
    """
    _version = '222'
    fluent_name = 'pb-disc'
    _python_name = 'pb_disc'
    child_object_type = pb_disc_child
    return_type = 'object'

class pb_qmom_bc_child(String, AllowedValuesMixin):
    """
    'child_object_type' of pb_qmom_bc.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'pb_qmom_bc_child'
    return_type = 'object'

class pb_qmom_bc(NamedObject[pb_qmom_bc_child], CreatableNamedObjectMixinOld[pb_qmom_bc_child]):
    """
    'pb_qmom_bc' child.
    """
    _version = '222'
    fluent_name = 'pb-qmom-bc'
    _python_name = 'pb_qmom_bc'
    child_object_type = pb_qmom_bc_child
    return_type = 'object'

class pb_qmom_child(Group):
    """
    'child_object_type' of pb_qmom.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'pb_qmom_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pb_qmom(NamedObject[pb_qmom_child], CreatableNamedObjectMixinOld[pb_qmom_child]):
    """
    'pb_qmom' child.
    """
    _version = '222'
    fluent_name = 'pb-qmom'
    _python_name = 'pb_qmom'
    child_object_type = pb_qmom_child
    return_type = 'object'

class pb_smm_bc_child(String, AllowedValuesMixin):
    """
    'child_object_type' of pb_smm_bc.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'pb_smm_bc_child'
    return_type = 'object'

class pb_smm_bc(NamedObject[pb_smm_bc_child], CreatableNamedObjectMixinOld[pb_smm_bc_child]):
    """
    'pb_smm_bc' child.
    """
    _version = '222'
    fluent_name = 'pb-smm-bc'
    _python_name = 'pb_smm_bc'
    child_object_type = pb_smm_bc_child
    return_type = 'object'

class pb_smm_child(Group):
    """
    'child_object_type' of pb_smm.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'pb_smm_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pb_smm(NamedObject[pb_smm_child], CreatableNamedObjectMixinOld[pb_smm_child]):
    """
    'pb_smm' child.
    """
    _version = '222'
    fluent_name = 'pb-smm'
    _python_name = 'pb_smm'
    child_object_type = pb_smm_child
    return_type = 'object'

class pb_dqmom_bc_child(String, AllowedValuesMixin):
    """
    'child_object_type' of pb_dqmom_bc.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'pb_dqmom_bc_child'
    return_type = 'object'

class pb_dqmom_bc(NamedObject[pb_dqmom_bc_child], CreatableNamedObjectMixinOld[pb_dqmom_bc_child]):
    """
    'pb_dqmom_bc' child.
    """
    _version = '222'
    fluent_name = 'pb-dqmom-bc'
    _python_name = 'pb_dqmom_bc'
    child_object_type = pb_dqmom_bc_child
    return_type = 'object'

class pb_dqmom_child(Group):
    """
    'child_object_type' of pb_dqmom.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'pb_dqmom_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pb_dqmom(NamedObject[pb_dqmom_child], CreatableNamedObjectMixinOld[pb_dqmom_child]):
    """
    'pb_dqmom' child.
    """
    _version = '222'
    fluent_name = 'pb-dqmom'
    _python_name = 'pb_dqmom'
    child_object_type = pb_dqmom_child
    return_type = 'object'

class dpm_bc_type(String, AllowedValuesMixin):
    """
    'dpm_bc_type' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-type'
    _python_name = 'dpm_bc_type'
    return_type = 'object'

class dpm_bc_collision_partner(String, AllowedValuesMixin):
    """
    'dpm_bc_collision_partner' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-collision-partner'
    _python_name = 'dpm_bc_collision_partner'
    return_type = 'object'

class reinj_inj(String, AllowedValuesMixin):
    """
    'reinj_inj' child.
    """
    _version = '222'
    fluent_name = 'reinj-inj'
    _python_name = 'reinj_inj'
    return_type = 'object'

class dpm_bc_udf(String, AllowedValuesMixin):
    """
    'dpm_bc_udf' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-udf'
    _python_name = 'dpm_bc_udf'
    return_type = 'object'

class mixing_plane_thread(Boolean, AllowedValuesMixin):
    """
    'mixing_plane_thread' child.
    """
    _version = '222'
    fluent_name = 'mixing-plane-thread?'
    _python_name = 'mixing_plane_thread'
    return_type = 'object'

class ac_options(String, AllowedValuesMixin):
    """
    'ac_options' child.
    """
    _version = '222'
    fluent_name = 'ac-options'
    _python_name = 'ac_options'
    return_type = 'object'

class p_backflow_spec(String, AllowedValuesMixin):
    """
    'p_backflow_spec' child.
    """
    _version = '222'
    fluent_name = 'p-backflow-spec'
    _python_name = 'p_backflow_spec'
    return_type = 'object'

class p_backflow_spec_gen(String, AllowedValuesMixin):
    """
    'p_backflow_spec_gen' child.
    """
    _version = '222'
    fluent_name = 'p-backflow-spec-gen'
    _python_name = 'p_backflow_spec_gen'
    return_type = 'object'

class impedance_0(Real, AllowedValuesMixin):
    """
    'impedance_0' child.
    """
    _version = '222'
    fluent_name = 'impedance-0'
    _python_name = 'impedance_0'
    return_type = 'object'

class pole(Real, AllowedValuesMixin):
    """
    'pole' child.
    """
    _version = '222'
    fluent_name = 'pole'
    _python_name = 'pole'
    return_type = 'object'

class amplitude(Real, AllowedValuesMixin):
    """
    'amplitude' child.
    """
    _version = '222'
    fluent_name = 'amplitude'
    _python_name = 'amplitude'
    return_type = 'object'

class impedance_1_child(Group):
    """
    'child_object_type' of impedance_1.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'impedance_1_child'
    child_names = ['pole', 'amplitude']
    _child_classes = dict(
        pole=pole,
        amplitude=amplitude,
    )
    return_type = 'object'

class impedance_1(ListObject[impedance_1_child]):
    """
    'impedance_1' child.
    """
    _version = '222'
    fluent_name = 'impedance-1'
    _python_name = 'impedance_1'
    child_object_type = impedance_1_child
    return_type = 'object'

class pole_real(Real, AllowedValuesMixin):
    """
    'pole_real' child.
    """
    _version = '222'
    fluent_name = 'pole-real'
    _python_name = 'pole_real'
    return_type = 'object'

class pole_imag(Real, AllowedValuesMixin):
    """
    'pole_imag' child.
    """
    _version = '222'
    fluent_name = 'pole-imag'
    _python_name = 'pole_imag'
    return_type = 'object'

class amplitude_real(Real, AllowedValuesMixin):
    """
    'amplitude_real' child.
    """
    _version = '222'
    fluent_name = 'amplitude-real'
    _python_name = 'amplitude_real'
    return_type = 'object'

class amplitude_imag(Real, AllowedValuesMixin):
    """
    'amplitude_imag' child.
    """
    _version = '222'
    fluent_name = 'amplitude-imag'
    _python_name = 'amplitude_imag'
    return_type = 'object'

class impedance_2_child(Group):
    """
    'child_object_type' of impedance_2.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'impedance_2_child'
    child_names = ['pole_real', 'pole_imag', 'amplitude_real', 'amplitude_imag']
    _child_classes = dict(
        pole_real=pole_real,
        pole_imag=pole_imag,
        amplitude_real=amplitude_real,
        amplitude_imag=amplitude_imag,
    )
    return_type = 'object'

class impedance_2(ListObject[impedance_2_child]):
    """
    'impedance_2' child.
    """
    _version = '222'
    fluent_name = 'impedance-2'
    _python_name = 'impedance_2'
    child_object_type = impedance_2_child
    return_type = 'object'

class ac_wave(Group):
    """
    'ac_wave' child.
    """
    _version = '222'
    fluent_name = 'ac-wave'
    _python_name = 'ac_wave'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class prevent_reverse_flow(Boolean, AllowedValuesMixin):
    """
    'prevent_reverse_flow' child.
    """
    _version = '222'
    fluent_name = 'prevent-reverse-flow?'
    _python_name = 'prevent_reverse_flow'
    return_type = 'object'

class radial(Boolean, AllowedValuesMixin):
    """
    'radial' child.
    """
    _version = '222'
    fluent_name = 'radial?'
    _python_name = 'radial'
    return_type = 'object'

class avg_press_spec(Boolean, AllowedValuesMixin):
    """
    'avg_press_spec' child.
    """
    _version = '222'
    fluent_name = 'avg-press-spec?'
    _python_name = 'avg_press_spec'
    return_type = 'object'

class press_averaging_method(Integer, AllowedValuesMixin):
    """
    'press_averaging_method' child.
    """
    _version = '222'
    fluent_name = 'press-averaging-method'
    _python_name = 'press_averaging_method'
    return_type = 'object'

class targeted_mf_boundary(Boolean, AllowedValuesMixin):
    """
    'targeted_mf_boundary' child.
    """
    _version = '222'
    fluent_name = 'targeted-mf-boundary?'
    _python_name = 'targeted_mf_boundary'
    return_type = 'object'

class targeted_mf(Group):
    """
    'targeted_mf' child.
    """
    _version = '222'
    fluent_name = 'targeted-mf'
    _python_name = 'targeted_mf'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class targeted_mf_pmax(Group):
    """
    'targeted_mf_pmax' child.
    """
    _version = '222'
    fluent_name = 'targeted-mf-pmax'
    _python_name = 'targeted_mf_pmax'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class targeted_mf_pmin(Group):
    """
    'targeted_mf_pmin' child.
    """
    _version = '222'
    fluent_name = 'targeted-mf-pmin'
    _python_name = 'targeted_mf_pmin'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class gen_nrbc_spec(String, AllowedValuesMixin):
    """
    'gen_nrbc_spec' child.
    """
    _version = '222'
    fluent_name = 'gen-nrbc-spec'
    _python_name = 'gen_nrbc_spec'
    return_type = 'object'

class wsf(Group):
    """
    'wsf' child.
    """
    _version = '222'
    fluent_name = 'wsf'
    _python_name = 'wsf'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class wsb(Group):
    """
    'wsb' child.
    """
    _version = '222'
    fluent_name = 'wsb'
    _python_name = 'wsb'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class wsn(Group):
    """
    'wsn' child.
    """
    _version = '222'
    fluent_name = 'wsn'
    _python_name = 'wsn'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class solar_fluxes(Boolean, AllowedValuesMixin):
    """
    'solar_fluxes' child.
    """
    _version = '222'
    fluent_name = 'solar-fluxes?'
    _python_name = 'solar_fluxes'
    return_type = 'object'

class solar_shining_factor(Real, AllowedValuesMixin):
    """
    'solar_shining_factor' child.
    """
    _version = '222'
    fluent_name = 'solar-shining-factor'
    _python_name = 'solar_shining_factor'
    return_type = 'object'

class radiating_s2s_surface(Boolean, AllowedValuesMixin):
    """
    'radiating_s2s_surface' child.
    """
    _version = '222'
    fluent_name = 'radiating-s2s-surface?'
    _python_name = 'radiating_s2s_surface'
    return_type = 'object'

class a(Group):
    """
    'a' child.
    """
    _version = '222'
    fluent_name = 'a'
    _python_name = 'a'
    child_names = ['method', 'number_of_coeff', 'function_of', 'coefficients', 'constant', 'piecewise_polynomial', 'piecewise_linear']
    _child_classes = dict(
        method=method,
        number_of_coeff=number_of_coeff,
        function_of=function_of,
        coefficients=coefficients,
        constant=constant,
        piecewise_polynomial=piecewise_polynomial,
        piecewise_linear=piecewise_linear,
    )
    return_type = 'object'

class strength(Group):
    """
    'strength' child.
    """
    _version = '222'
    fluent_name = 'strength'
    _python_name = 'strength'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class new_fan_definition(Boolean, AllowedValuesMixin):
    """
    'new_fan_definition' child.
    """
    _version = '222'
    fluent_name = 'new-fan-definition?'
    _python_name = 'new_fan_definition'
    return_type = 'object'

class phase_3_child(Group):
    """
    'child_object_type' of phase.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'phase_child'
    child_names = ['geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'open_channel', 'outlet_number', 'pressure_spec_method', 'press_spec', 'frame_of_reference', 'phase_spec', 'ht_local', 'p', 'p_profile_multiplier', 'ht_bottom', 'den_spec', 't0', 'direction_spec', 'coordinate_system', 'flow_direction_component', 'axis_direction_component', 'axis_origin_component', 'ke_spec', 'nut', 'kl', 'intermit', 'k', 'e', 'o', 'v2', 'turb_intensity', 'turb_length_scale', 'turb_hydraulic_diam', 'turb_viscosity_ratio', 'turb_viscosity_ratio_profile', 'rst_spec', 'uu', 'vv', 'ww', 'uv', 'vw', 'uw', 'ksgs_spec', 'ksgs', 'sgs_turb_intensity', 'radiation_bc', 'radial_direction_component', 'coll_dtheta', 'coll_dphi', 'band_q_irrad', 'band_q_irrad_diffuse', 'parallel_collimated_beam', 'solar_direction', 'solar_irradiation', 't_b_b_spec', 't_b_b', 'in_emiss', 'fmean', 'fmean2', 'fvar', 'fvar2', 'granular_temperature', 'iac', 'lsfun', 'vof_spec', 'volume_fraction', 'species_in_mole_fractions', 'mf', 'elec_potential_type', 'potential_value', 'dual_potential_type', 'dual_potential_value', 'x_displacement_type', 'x_displacement_value', 'y_displacement_type', 'y_displacement_value', 'z_displacement_type', 'z_displacement_value', 'prob_mode_1', 'prob_mode_2', 'prob_mode_3', 'premixc', 'premixc_var', 'ecfm_sigma', 'inert', 'pollut_no', 'pollut_hcn', 'pollut_nh3', 'pollut_n2o', 'pollut_urea', 'pollut_hnco', 'pollut_nco', 'pollut_so2', 'pollut_h2s', 'pollut_so3', 'pollut_sh', 'pollut_so', 'pollut_soot', 'pollut_nuclei', 'pollut_ctar', 'pollut_hg', 'pollut_hgcl2', 'pollut_hcl', 'pollut_hgo', 'pollut_cl', 'pollut_cl2', 'pollut_hgcl', 'pollut_hocl', 'tss_scalar', 'fensapice_flow_bc_subtype', 'uds_bc', 'uds', 'pb_disc_bc', 'pb_disc', 'pb_qmom_bc', 'pb_qmom', 'pb_smm_bc', 'pb_smm', 'pb_dqmom_bc', 'pb_dqmom', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'mixing_plane_thread', 'ac_options', 'p_backflow_spec', 'p_backflow_spec_gen', 'impedance_0', 'impedance_1', 'impedance_2', 'ac_wave', 'prevent_reverse_flow', 'radial', 'avg_press_spec', 'press_averaging_method', 'targeted_mf_boundary', 'targeted_mf', 'targeted_mf_pmax', 'targeted_mf_pmin', 'gen_nrbc_spec', 'wsf', 'wsb', 'wsn', 'solar_fluxes', 'solar_shining_factor', 'radiating_s2s_surface', 'a', 'strength', 'new_fan_definition']
    _child_classes = dict(
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        open_channel=open_channel,
        outlet_number=outlet_number,
        pressure_spec_method=pressure_spec_method,
        press_spec=press_spec,
        frame_of_reference=frame_of_reference,
        phase_spec=phase_spec,
        ht_local=ht_local,
        p=p,
        p_profile_multiplier=p_profile_multiplier,
        ht_bottom=ht_bottom,
        den_spec=den_spec,
        t0=t0,
        direction_spec=direction_spec,
        coordinate_system=coordinate_system,
        flow_direction_component=flow_direction_component,
        axis_direction_component=axis_direction_component_1,
        axis_origin_component=axis_origin_component_1,
        ke_spec=ke_spec,
        nut=nut,
        kl=kl,
        intermit=intermit,
        k=k,
        e=e,
        o=o,
        v2=v2,
        turb_intensity=turb_intensity,
        turb_length_scale=turb_length_scale,
        turb_hydraulic_diam=turb_hydraulic_diam,
        turb_viscosity_ratio=turb_viscosity_ratio,
        turb_viscosity_ratio_profile=turb_viscosity_ratio_profile,
        rst_spec=rst_spec,
        uu=uu,
        vv=vv,
        ww=ww,
        uv=uv,
        vw=vw,
        uw=uw,
        ksgs_spec=ksgs_spec,
        ksgs=ksgs,
        sgs_turb_intensity=sgs_turb_intensity,
        radiation_bc=radiation_bc,
        radial_direction_component=radial_direction_component,
        coll_dtheta=coll_dtheta,
        coll_dphi=coll_dphi,
        band_q_irrad=band_q_irrad,
        band_q_irrad_diffuse=band_q_irrad_diffuse,
        parallel_collimated_beam=parallel_collimated_beam,
        solar_direction=solar_direction,
        solar_irradiation=solar_irradiation,
        t_b_b_spec=t_b_b_spec,
        t_b_b=t_b_b,
        in_emiss=in_emiss,
        fmean=fmean,
        fmean2=fmean2,
        fvar=fvar,
        fvar2=fvar2,
        granular_temperature=granular_temperature,
        iac=iac,
        lsfun=lsfun,
        vof_spec=vof_spec,
        volume_fraction=volume_fraction,
        species_in_mole_fractions=species_in_mole_fractions,
        mf=mf,
        elec_potential_type=elec_potential_type,
        potential_value=potential_value,
        dual_potential_type=dual_potential_type,
        dual_potential_value=dual_potential_value,
        x_displacement_type=x_displacement_type,
        x_displacement_value=x_displacement_value,
        y_displacement_type=y_displacement_type,
        y_displacement_value=y_displacement_value,
        z_displacement_type=z_displacement_type,
        z_displacement_value=z_displacement_value,
        prob_mode_1=prob_mode_1,
        prob_mode_2=prob_mode_2,
        prob_mode_3=prob_mode_3,
        premixc=premixc,
        premixc_var=premixc_var,
        ecfm_sigma=ecfm_sigma,
        inert=inert,
        pollut_no=pollut_no,
        pollut_hcn=pollut_hcn,
        pollut_nh3=pollut_nh3,
        pollut_n2o=pollut_n2o,
        pollut_urea=pollut_urea,
        pollut_hnco=pollut_hnco,
        pollut_nco=pollut_nco,
        pollut_so2=pollut_so2,
        pollut_h2s=pollut_h2s,
        pollut_so3=pollut_so3,
        pollut_sh=pollut_sh,
        pollut_so=pollut_so,
        pollut_soot=pollut_soot,
        pollut_nuclei=pollut_nuclei,
        pollut_ctar=pollut_ctar,
        pollut_hg=pollut_hg,
        pollut_hgcl2=pollut_hgcl2,
        pollut_hcl=pollut_hcl,
        pollut_hgo=pollut_hgo,
        pollut_cl=pollut_cl,
        pollut_cl2=pollut_cl2,
        pollut_hgcl=pollut_hgcl,
        pollut_hocl=pollut_hocl,
        tss_scalar=tss_scalar,
        fensapice_flow_bc_subtype=fensapice_flow_bc_subtype,
        uds_bc=uds_bc,
        uds=uds,
        pb_disc_bc=pb_disc_bc,
        pb_disc=pb_disc,
        pb_qmom_bc=pb_qmom_bc,
        pb_qmom=pb_qmom,
        pb_smm_bc=pb_smm_bc,
        pb_smm=pb_smm,
        pb_dqmom_bc=pb_dqmom_bc,
        pb_dqmom=pb_dqmom,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        mixing_plane_thread=mixing_plane_thread,
        ac_options=ac_options,
        p_backflow_spec=p_backflow_spec,
        p_backflow_spec_gen=p_backflow_spec_gen,
        impedance_0=impedance_0,
        impedance_1=impedance_1,
        impedance_2=impedance_2,
        ac_wave=ac_wave,
        prevent_reverse_flow=prevent_reverse_flow,
        radial=radial,
        avg_press_spec=avg_press_spec,
        press_averaging_method=press_averaging_method,
        targeted_mf_boundary=targeted_mf_boundary,
        targeted_mf=targeted_mf,
        targeted_mf_pmax=targeted_mf_pmax,
        targeted_mf_pmin=targeted_mf_pmin,
        gen_nrbc_spec=gen_nrbc_spec,
        wsf=wsf,
        wsb=wsb,
        wsn=wsn,
        solar_fluxes=solar_fluxes,
        solar_shining_factor=solar_shining_factor,
        radiating_s2s_surface=radiating_s2s_surface,
        a=a,
        strength=strength,
        new_fan_definition=new_fan_definition,
    )
    return_type = 'object'

class phase_3(NamedObject[phase_3_child], CreatableNamedObjectMixinOld[phase_3_child]):
    """
    'phase' child.
    """
    _version = '222'
    fluent_name = 'phase'
    _python_name = 'phase'
    child_object_type = phase_3_child
    return_type = 'object'

class exhaust_fan_child(Group):
    """
    'child_object_type' of exhaust_fan.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'exhaust_fan_child'
    child_names = ['phase', 'geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'open_channel', 'outlet_number', 'pressure_spec_method', 'press_spec', 'frame_of_reference', 'phase_spec', 'ht_local', 'p', 'p_profile_multiplier', 'ht_bottom', 'den_spec', 't0', 'direction_spec', 'coordinate_system', 'flow_direction_component', 'axis_direction_component', 'axis_origin_component', 'ke_spec', 'nut', 'kl', 'intermit', 'k', 'e', 'o', 'v2', 'turb_intensity', 'turb_length_scale', 'turb_hydraulic_diam', 'turb_viscosity_ratio', 'turb_viscosity_ratio_profile', 'rst_spec', 'uu', 'vv', 'ww', 'uv', 'vw', 'uw', 'ksgs_spec', 'ksgs', 'sgs_turb_intensity', 'radiation_bc', 'radial_direction_component', 'coll_dtheta', 'coll_dphi', 'band_q_irrad', 'band_q_irrad_diffuse', 'parallel_collimated_beam', 'solar_direction', 'solar_irradiation', 't_b_b_spec', 't_b_b', 'in_emiss', 'fmean', 'fmean2', 'fvar', 'fvar2', 'granular_temperature', 'iac', 'lsfun', 'vof_spec', 'volume_fraction', 'species_in_mole_fractions', 'mf', 'elec_potential_type', 'potential_value', 'dual_potential_type', 'dual_potential_value', 'x_displacement_type', 'x_displacement_value', 'y_displacement_type', 'y_displacement_value', 'z_displacement_type', 'z_displacement_value', 'prob_mode_1', 'prob_mode_2', 'prob_mode_3', 'premixc', 'premixc_var', 'ecfm_sigma', 'inert', 'pollut_no', 'pollut_hcn', 'pollut_nh3', 'pollut_n2o', 'pollut_urea', 'pollut_hnco', 'pollut_nco', 'pollut_so2', 'pollut_h2s', 'pollut_so3', 'pollut_sh', 'pollut_so', 'pollut_soot', 'pollut_nuclei', 'pollut_ctar', 'pollut_hg', 'pollut_hgcl2', 'pollut_hcl', 'pollut_hgo', 'pollut_cl', 'pollut_cl2', 'pollut_hgcl', 'pollut_hocl', 'tss_scalar', 'fensapice_flow_bc_subtype', 'uds_bc', 'uds', 'pb_disc_bc', 'pb_disc', 'pb_qmom_bc', 'pb_qmom', 'pb_smm_bc', 'pb_smm', 'pb_dqmom_bc', 'pb_dqmom', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'mixing_plane_thread', 'ac_options', 'p_backflow_spec', 'p_backflow_spec_gen', 'impedance_0', 'impedance_1', 'impedance_2', 'ac_wave', 'prevent_reverse_flow', 'radial', 'avg_press_spec', 'press_averaging_method', 'targeted_mf_boundary', 'targeted_mf', 'targeted_mf_pmax', 'targeted_mf_pmin', 'gen_nrbc_spec', 'wsf', 'wsb', 'wsn', 'solar_fluxes', 'solar_shining_factor', 'radiating_s2s_surface', 'a', 'strength', 'new_fan_definition']
    _child_classes = dict(
        phase=phase_3,
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        open_channel=open_channel,
        outlet_number=outlet_number,
        pressure_spec_method=pressure_spec_method,
        press_spec=press_spec,
        frame_of_reference=frame_of_reference,
        phase_spec=phase_spec,
        ht_local=ht_local,
        p=p,
        p_profile_multiplier=p_profile_multiplier,
        ht_bottom=ht_bottom,
        den_spec=den_spec,
        t0=t0,
        direction_spec=direction_spec,
        coordinate_system=coordinate_system,
        flow_direction_component=flow_direction_component,
        axis_direction_component=axis_direction_component_1,
        axis_origin_component=axis_origin_component_1,
        ke_spec=ke_spec,
        nut=nut,
        kl=kl,
        intermit=intermit,
        k=k,
        e=e,
        o=o,
        v2=v2,
        turb_intensity=turb_intensity,
        turb_length_scale=turb_length_scale,
        turb_hydraulic_diam=turb_hydraulic_diam,
        turb_viscosity_ratio=turb_viscosity_ratio,
        turb_viscosity_ratio_profile=turb_viscosity_ratio_profile,
        rst_spec=rst_spec,
        uu=uu,
        vv=vv,
        ww=ww,
        uv=uv,
        vw=vw,
        uw=uw,
        ksgs_spec=ksgs_spec,
        ksgs=ksgs,
        sgs_turb_intensity=sgs_turb_intensity,
        radiation_bc=radiation_bc,
        radial_direction_component=radial_direction_component,
        coll_dtheta=coll_dtheta,
        coll_dphi=coll_dphi,
        band_q_irrad=band_q_irrad,
        band_q_irrad_diffuse=band_q_irrad_diffuse,
        parallel_collimated_beam=parallel_collimated_beam,
        solar_direction=solar_direction,
        solar_irradiation=solar_irradiation,
        t_b_b_spec=t_b_b_spec,
        t_b_b=t_b_b,
        in_emiss=in_emiss,
        fmean=fmean,
        fmean2=fmean2,
        fvar=fvar,
        fvar2=fvar2,
        granular_temperature=granular_temperature,
        iac=iac,
        lsfun=lsfun,
        vof_spec=vof_spec,
        volume_fraction=volume_fraction,
        species_in_mole_fractions=species_in_mole_fractions,
        mf=mf,
        elec_potential_type=elec_potential_type,
        potential_value=potential_value,
        dual_potential_type=dual_potential_type,
        dual_potential_value=dual_potential_value,
        x_displacement_type=x_displacement_type,
        x_displacement_value=x_displacement_value,
        y_displacement_type=y_displacement_type,
        y_displacement_value=y_displacement_value,
        z_displacement_type=z_displacement_type,
        z_displacement_value=z_displacement_value,
        prob_mode_1=prob_mode_1,
        prob_mode_2=prob_mode_2,
        prob_mode_3=prob_mode_3,
        premixc=premixc,
        premixc_var=premixc_var,
        ecfm_sigma=ecfm_sigma,
        inert=inert,
        pollut_no=pollut_no,
        pollut_hcn=pollut_hcn,
        pollut_nh3=pollut_nh3,
        pollut_n2o=pollut_n2o,
        pollut_urea=pollut_urea,
        pollut_hnco=pollut_hnco,
        pollut_nco=pollut_nco,
        pollut_so2=pollut_so2,
        pollut_h2s=pollut_h2s,
        pollut_so3=pollut_so3,
        pollut_sh=pollut_sh,
        pollut_so=pollut_so,
        pollut_soot=pollut_soot,
        pollut_nuclei=pollut_nuclei,
        pollut_ctar=pollut_ctar,
        pollut_hg=pollut_hg,
        pollut_hgcl2=pollut_hgcl2,
        pollut_hcl=pollut_hcl,
        pollut_hgo=pollut_hgo,
        pollut_cl=pollut_cl,
        pollut_cl2=pollut_cl2,
        pollut_hgcl=pollut_hgcl,
        pollut_hocl=pollut_hocl,
        tss_scalar=tss_scalar,
        fensapice_flow_bc_subtype=fensapice_flow_bc_subtype,
        uds_bc=uds_bc,
        uds=uds,
        pb_disc_bc=pb_disc_bc,
        pb_disc=pb_disc,
        pb_qmom_bc=pb_qmom_bc,
        pb_qmom=pb_qmom,
        pb_smm_bc=pb_smm_bc,
        pb_smm=pb_smm,
        pb_dqmom_bc=pb_dqmom_bc,
        pb_dqmom=pb_dqmom,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        mixing_plane_thread=mixing_plane_thread,
        ac_options=ac_options,
        p_backflow_spec=p_backflow_spec,
        p_backflow_spec_gen=p_backflow_spec_gen,
        impedance_0=impedance_0,
        impedance_1=impedance_1,
        impedance_2=impedance_2,
        ac_wave=ac_wave,
        prevent_reverse_flow=prevent_reverse_flow,
        radial=radial,
        avg_press_spec=avg_press_spec,
        press_averaging_method=press_averaging_method,
        targeted_mf_boundary=targeted_mf_boundary,
        targeted_mf=targeted_mf,
        targeted_mf_pmax=targeted_mf_pmax,
        targeted_mf_pmin=targeted_mf_pmin,
        gen_nrbc_spec=gen_nrbc_spec,
        wsf=wsf,
        wsb=wsb,
        wsn=wsn,
        solar_fluxes=solar_fluxes,
        solar_shining_factor=solar_shining_factor,
        radiating_s2s_surface=radiating_s2s_surface,
        a=a,
        strength=strength,
        new_fan_definition=new_fan_definition,
    )
    return_type = 'object'

class exhaust_fan(NamedObject[exhaust_fan_child], CreatableNamedObjectMixinOld[exhaust_fan_child]):
    """
    'exhaust_fan' child.
    """
    _version = '222'
    fluent_name = 'exhaust-fan'
    _python_name = 'exhaust_fan'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = exhaust_fan_child
    return_type = 'object'

class porous_jump_turb_wall_treatment(Boolean, AllowedValuesMixin):
    """
    'porous_jump_turb_wall_treatment' child.
    """
    _version = '222'
    fluent_name = 'porous-jump-turb-wall-treatment?'
    _python_name = 'porous_jump_turb_wall_treatment'
    return_type = 'object'

class dir(Integer, AllowedValuesMixin):
    """
    'dir' child.
    """
    _version = '222'
    fluent_name = 'dir'
    _python_name = 'dir'
    return_type = 'object'

class average_dp(Boolean, AllowedValuesMixin):
    """
    'average_dp' child.
    """
    _version = '222'
    fluent_name = 'average-dp?'
    _python_name = 'average_dp'
    return_type = 'object'

class c(Group):
    """
    'c' child.
    """
    _version = '222'
    fluent_name = 'c'
    _python_name = 'c'
    child_names = ['method', 'number_of_coeff', 'function_of', 'coefficients', 'constant', 'piecewise_polynomial', 'piecewise_linear']
    _child_classes = dict(
        method=method,
        number_of_coeff=number_of_coeff,
        function_of=function_of,
        coefficients=coefficients,
        constant=constant,
        piecewise_polynomial=piecewise_polynomial,
        piecewise_linear=piecewise_linear,
    )
    return_type = 'object'

class limit_range(Boolean, AllowedValuesMixin):
    """
    'limit_range' child.
    """
    _version = '222'
    fluent_name = 'limit-range?'
    _python_name = 'limit_range'
    return_type = 'object'

class v_min(Real, AllowedValuesMixin):
    """
    'v_min' child.
    """
    _version = '222'
    fluent_name = 'v-min'
    _python_name = 'v_min'
    return_type = 'object'

class v_max(Real, AllowedValuesMixin):
    """
    'v_max' child.
    """
    _version = '222'
    fluent_name = 'v-max'
    _python_name = 'v_max'
    return_type = 'object'

class profile_dp(Boolean, AllowedValuesMixin):
    """
    'profile_dp' child.
    """
    _version = '222'
    fluent_name = 'profile-dp?'
    _python_name = 'profile_dp'
    return_type = 'object'

class dp_profile(Group):
    """
    'dp_profile' child.
    """
    _version = '222'
    fluent_name = 'dp-profile'
    _python_name = 'dp_profile'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class swirl_model(Boolean, AllowedValuesMixin):
    """
    'swirl_model' child.
    """
    _version = '222'
    fluent_name = 'swirl-model?'
    _python_name = 'swirl_model'
    return_type = 'object'

class fan_vr(Real, AllowedValuesMixin):
    """
    'fan_vr' child.
    """
    _version = '222'
    fluent_name = 'fan-vr'
    _python_name = 'fan_vr'
    return_type = 'object'

class fr(Real, AllowedValuesMixin):
    """
    'fr' child.
    """
    _version = '222'
    fluent_name = 'fr'
    _python_name = 'fr'
    return_type = 'object'

class hub(Real, AllowedValuesMixin):
    """
    'hub' child.
    """
    _version = '222'
    fluent_name = 'hub'
    _python_name = 'hub'
    return_type = 'object'

class profile_vt(Boolean, AllowedValuesMixin):
    """
    'profile_vt' child.
    """
    _version = '222'
    fluent_name = 'profile-vt?'
    _python_name = 'profile_vt'
    return_type = 'object'

class vt_profile(Group):
    """
    'vt_profile' child.
    """
    _version = '222'
    fluent_name = 'vt-profile'
    _python_name = 'vt_profile'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class profile_vr(Boolean, AllowedValuesMixin):
    """
    'profile_vr' child.
    """
    _version = '222'
    fluent_name = 'profile-vr?'
    _python_name = 'profile_vr'
    return_type = 'object'

class vr_profile(Group):
    """
    'vr_profile' child.
    """
    _version = '222'
    fluent_name = 'vr-profile'
    _python_name = 'vr_profile'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class swirl_factor(Real, AllowedValuesMixin):
    """
    'swirl_factor' child.
    """
    _version = '222'
    fluent_name = 'swirl-factor'
    _python_name = 'swirl_factor'
    return_type = 'object'

class phase_4_child(Group):
    """
    'child_object_type' of phase.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'phase_child'
    child_names = ['geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'porous_jump_turb_wall_treatment', 'dir', 'average_dp', 'c', 'limit_range', 'v_min', 'v_max', 'strength', 'profile_dp', 'dp_profile', 'swirl_model', 'fan_vr', 'fr', 'hub', 'axis_origin_component', 'axis_direction_component', 'profile_vt', 'vt_profile', 'profile_vr', 'vr_profile', 'swirl_factor', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'new_fan_definition']
    _child_classes = dict(
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        porous_jump_turb_wall_treatment=porous_jump_turb_wall_treatment,
        dir=dir,
        average_dp=average_dp,
        c=c,
        limit_range=limit_range,
        v_min=v_min,
        v_max=v_max,
        strength=strength,
        profile_dp=profile_dp,
        dp_profile=dp_profile,
        swirl_model=swirl_model,
        fan_vr=fan_vr,
        fr=fr,
        hub=hub,
        axis_origin_component=axis_origin_component_1,
        axis_direction_component=axis_direction_component_1,
        profile_vt=profile_vt,
        vt_profile=vt_profile,
        profile_vr=profile_vr,
        vr_profile=vr_profile,
        swirl_factor=swirl_factor,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        new_fan_definition=new_fan_definition,
    )
    return_type = 'object'

class phase_4(NamedObject[phase_4_child], CreatableNamedObjectMixinOld[phase_4_child]):
    """
    'phase' child.
    """
    _version = '222'
    fluent_name = 'phase'
    _python_name = 'phase'
    child_object_type = phase_4_child
    return_type = 'object'

class fan_child(Group):
    """
    'child_object_type' of fan.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'fan_child'
    child_names = ['phase', 'geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'porous_jump_turb_wall_treatment', 'dir', 'average_dp', 'c', 'limit_range', 'v_min', 'v_max', 'strength', 'profile_dp', 'dp_profile', 'swirl_model', 'fan_vr', 'fr', 'hub', 'axis_origin_component', 'axis_direction_component', 'profile_vt', 'vt_profile', 'profile_vr', 'vr_profile', 'swirl_factor', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'new_fan_definition']
    _child_classes = dict(
        phase=phase_4,
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        porous_jump_turb_wall_treatment=porous_jump_turb_wall_treatment,
        dir=dir,
        average_dp=average_dp,
        c=c,
        limit_range=limit_range,
        v_min=v_min,
        v_max=v_max,
        strength=strength,
        profile_dp=profile_dp,
        dp_profile=dp_profile,
        swirl_model=swirl_model,
        fan_vr=fan_vr,
        fr=fr,
        hub=hub,
        axis_origin_component=axis_origin_component_1,
        axis_direction_component=axis_direction_component_1,
        profile_vt=profile_vt,
        vt_profile=vt_profile,
        profile_vr=profile_vr,
        vr_profile=vr_profile,
        swirl_factor=swirl_factor,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        new_fan_definition=new_fan_definition,
    )
    return_type = 'object'

class fan(NamedObject[fan_child], CreatableNamedObjectMixinOld[fan_child]):
    """
    'fan' child.
    """
    _version = '222'
    fluent_name = 'fan'
    _python_name = 'fan'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = fan_child
    return_type = 'object'

class geometry_child(Group):
    """
    'child_object_type' of geometry.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'geometry_child'
    child_names = ['phase', 'geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread']
    _child_classes = dict(
        phase=phase_2,
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
    )
    return_type = 'object'

class geometry(NamedObject[geometry_child], CreatableNamedObjectMixinOld[geometry_child]):
    """
    'geometry' child.
    """
    _version = '222'
    fluent_name = 'geometry'
    _python_name = 'geometry'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = geometry_child
    return_type = 'object'

class inlet_number(Integer, AllowedValuesMixin):
    """
    'inlet_number' child.
    """
    _version = '222'
    fluent_name = 'inlet-number'
    _python_name = 'inlet_number'
    return_type = 'object'

class p0(Group):
    """
    'p0' child.
    """
    _version = '222'
    fluent_name = 'p0'
    _python_name = 'p0'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class supersonic_or_initial_gauge_pressure(Group):
    """
    'supersonic_or_initial_gauge_pressure' child.
    """
    _version = '222'
    fluent_name = 'supersonic-or-initial-gauge-pressure'
    _python_name = 'supersonic_or_initial_gauge_pressure'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class flow_spec(String, AllowedValuesMixin):
    """
    'flow_spec' child.
    """
    _version = '222'
    fluent_name = 'flow-spec'
    _python_name = 'flow_spec'
    return_type = 'object'

class ht_total(Group):
    """
    'ht_total' child.
    """
    _version = '222'
    fluent_name = 'ht-total'
    _python_name = 'ht_total'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class vmag(Group):
    """
    'vmag' child.
    """
    _version = '222'
    fluent_name = 'vmag'
    _python_name = 'vmag'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class direction_vector_components_child(Group):
    """
    'child_object_type' of direction_vector_components.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'direction_vector_components_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class direction_vector_components(ListObject[direction_vector_components_child]):
    """
    'direction_vector_components' child.
    """
    _version = '222'
    fluent_name = 'direction-vector-components'
    _python_name = 'direction_vector_components'
    child_object_type = direction_vector_components_child
    return_type = 'object'

class les_spec_name(String, AllowedValuesMixin):
    """
    'les_spec_name' child.
    """
    _version = '222'
    fluent_name = 'les-spec-name'
    _python_name = 'les_spec_name'
    return_type = 'object'

class rfg_number_of_modes(Integer, AllowedValuesMixin):
    """
    'rfg_number_of_modes' child.
    """
    _version = '222'
    fluent_name = 'rfg-number-of-modes'
    _python_name = 'rfg_number_of_modes'
    return_type = 'object'

class vm_number_of_vortices(Integer, AllowedValuesMixin):
    """
    'vm_number_of_vortices' child.
    """
    _version = '222'
    fluent_name = 'vm-number-of-vortices'
    _python_name = 'vm_number_of_vortices'
    return_type = 'object'

class vm_streamwise_fluct(Boolean, AllowedValuesMixin):
    """
    'vm_streamwise_fluct' child.
    """
    _version = '222'
    fluent_name = 'vm-streamwise-fluct?'
    _python_name = 'vm_streamwise_fluct'
    return_type = 'object'

class vm_mass_conservation(Boolean, AllowedValuesMixin):
    """
    'vm_mass_conservation' child.
    """
    _version = '222'
    fluent_name = 'vm-mass-conservation?'
    _python_name = 'vm_mass_conservation'
    return_type = 'object'

class volumetric_synthetic_turbulence_generator(Boolean, AllowedValuesMixin):
    """
    'volumetric_synthetic_turbulence_generator' child.
    """
    _version = '222'
    fluent_name = 'volumetric-synthetic-turbulence-generator?'
    _python_name = 'volumetric_synthetic_turbulence_generator'
    return_type = 'object'

class volumetric_synthetic_turbulence_generator_option(String, AllowedValuesMixin):
    """
    'volumetric_synthetic_turbulence_generator_option' child.
    """
    _version = '222'
    fluent_name = 'volumetric-synthetic-turbulence-generator-option'
    _python_name = 'volumetric_synthetic_turbulence_generator_option'
    return_type = 'object'

class volumetric_synthetic_turbulence_generator_option_thickness(Real, AllowedValuesMixin):
    """
    'volumetric_synthetic_turbulence_generator_option_thickness' child.
    """
    _version = '222'
    fluent_name = 'volumetric-synthetic-turbulence-generator-option-thickness'
    _python_name = 'volumetric_synthetic_turbulence_generator_option_thickness'
    return_type = 'object'

class equ_required(Boolean, AllowedValuesMixin):
    """
    'equ_required' child.
    """
    _version = '222'
    fluent_name = 'equ-required?'
    _python_name = 'equ_required'
    return_type = 'object'

class fensapice_drop_bccustom(Boolean, AllowedValuesMixin):
    """
    'fensapice_drop_bccustom' child.
    """
    _version = '222'
    fluent_name = 'fensapice-drop-bccustom?'
    _python_name = 'fensapice_drop_bccustom'
    return_type = 'object'

class fensapice_drop_lwc(Real, AllowedValuesMixin):
    """
    'fensapice_drop_lwc' child.
    """
    _version = '222'
    fluent_name = 'fensapice-drop-lwc'
    _python_name = 'fensapice_drop_lwc'
    return_type = 'object'

class fensapice_drop_dtemp(Real, AllowedValuesMixin):
    """
    'fensapice_drop_dtemp' child.
    """
    _version = '222'
    fluent_name = 'fensapice-drop-dtemp'
    _python_name = 'fensapice_drop_dtemp'
    return_type = 'object'

class fensapice_drop_ddiam(Real, AllowedValuesMixin):
    """
    'fensapice_drop_ddiam' child.
    """
    _version = '222'
    fluent_name = 'fensapice-drop-ddiam'
    _python_name = 'fensapice_drop_ddiam'
    return_type = 'object'

class fensapice_drop_dv(Boolean, AllowedValuesMixin):
    """
    'fensapice_drop_dv' child.
    """
    _version = '222'
    fluent_name = 'fensapice-drop-dv?'
    _python_name = 'fensapice_drop_dv'
    return_type = 'object'

class fensapice_drop_dx(Real, AllowedValuesMixin):
    """
    'fensapice_drop_dx' child.
    """
    _version = '222'
    fluent_name = 'fensapice-drop-dx'
    _python_name = 'fensapice_drop_dx'
    return_type = 'object'

class fensapice_drop_dy(Real, AllowedValuesMixin):
    """
    'fensapice_drop_dy' child.
    """
    _version = '222'
    fluent_name = 'fensapice-drop-dy'
    _python_name = 'fensapice_drop_dy'
    return_type = 'object'

class fensapice_drop_dz(Real, AllowedValuesMixin):
    """
    'fensapice_drop_dz' child.
    """
    _version = '222'
    fluent_name = 'fensapice-drop-dz'
    _python_name = 'fensapice_drop_dz'
    return_type = 'object'

class fensapice_dpm_surface_injection(Boolean, AllowedValuesMixin):
    """
    'fensapice_dpm_surface_injection' child.
    """
    _version = '222'
    fluent_name = 'fensapice-dpm-surface-injection?'
    _python_name = 'fensapice_dpm_surface_injection'
    return_type = 'object'

class fensapice_dpm_inj_nstream(Integer, AllowedValuesMixin):
    """
    'fensapice_dpm_inj_nstream' child.
    """
    _version = '222'
    fluent_name = 'fensapice-dpm-inj-nstream'
    _python_name = 'fensapice_dpm_inj_nstream'
    return_type = 'object'

class fensapice_drop_icc(Real, AllowedValuesMixin):
    """
    'fensapice_drop_icc' child.
    """
    _version = '222'
    fluent_name = 'fensapice-drop-icc'
    _python_name = 'fensapice_drop_icc'
    return_type = 'object'

class fensapice_drop_ctemp(Real, AllowedValuesMixin):
    """
    'fensapice_drop_ctemp' child.
    """
    _version = '222'
    fluent_name = 'fensapice-drop-ctemp'
    _python_name = 'fensapice_drop_ctemp'
    return_type = 'object'

class fensapice_drop_cdiam(Real, AllowedValuesMixin):
    """
    'fensapice_drop_cdiam' child.
    """
    _version = '222'
    fluent_name = 'fensapice-drop-cdiam'
    _python_name = 'fensapice_drop_cdiam'
    return_type = 'object'

class fensapice_drop_cv(Boolean, AllowedValuesMixin):
    """
    'fensapice_drop_cv' child.
    """
    _version = '222'
    fluent_name = 'fensapice-drop-cv?'
    _python_name = 'fensapice_drop_cv'
    return_type = 'object'

class fensapice_drop_cx(Real, AllowedValuesMixin):
    """
    'fensapice_drop_cx' child.
    """
    _version = '222'
    fluent_name = 'fensapice-drop-cx'
    _python_name = 'fensapice_drop_cx'
    return_type = 'object'

class fensapice_drop_cy(Real, AllowedValuesMixin):
    """
    'fensapice_drop_cy' child.
    """
    _version = '222'
    fluent_name = 'fensapice-drop-cy'
    _python_name = 'fensapice_drop_cy'
    return_type = 'object'

class fensapice_drop_cz(Real, AllowedValuesMixin):
    """
    'fensapice_drop_cz' child.
    """
    _version = '222'
    fluent_name = 'fensapice-drop-cz'
    _python_name = 'fensapice_drop_cz'
    return_type = 'object'

class fensapice_drop_vrh(Boolean, AllowedValuesMixin):
    """
    'fensapice_drop_vrh' child.
    """
    _version = '222'
    fluent_name = 'fensapice-drop-vrh?'
    _python_name = 'fensapice_drop_vrh'
    return_type = 'object'

class fensapice_drop_vrh_1(Real, AllowedValuesMixin):
    """
    'fensapice_drop_vrh' child.
    """
    _version = '222'
    fluent_name = 'fensapice-drop-vrh'
    _python_name = 'fensapice_drop_vrh'
    return_type = 'object'

class fensapice_drop_vc(Real, AllowedValuesMixin):
    """
    'fensapice_drop_vc' child.
    """
    _version = '222'
    fluent_name = 'fensapice-drop-vc'
    _python_name = 'fensapice_drop_vc'
    return_type = 'object'

class les_spec(String, AllowedValuesMixin):
    """
    'les_spec' child.
    """
    _version = '222'
    fluent_name = 'les-spec'
    _python_name = 'les_spec'
    return_type = 'object'

class b(Group):
    """
    'b' child.
    """
    _version = '222'
    fluent_name = 'b'
    _python_name = 'b'
    child_names = ['method', 'number_of_coeff', 'function_of', 'coefficients', 'constant', 'piecewise_polynomial', 'piecewise_linear']
    _child_classes = dict(
        method=method,
        number_of_coeff=number_of_coeff,
        function_of=function_of,
        coefficients=coefficients,
        constant=constant,
        piecewise_polynomial=piecewise_polynomial,
        piecewise_linear=piecewise_linear,
    )
    return_type = 'object'

class phase_5_child(Group):
    """
    'child_object_type' of phase.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'phase_child'
    child_names = ['geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'open_channel', 'inlet_number', 'phase_spec', 'frame_of_reference', 'p0', 'supersonic_or_initial_gauge_pressure', 't0', 'direction_spec', 'flow_spec', 'ht_local', 'ht_total', 'vmag', 'ht_bottom', 'den_spec', 'coordinate_system', 'flow_direction_component', 'direction_vector_components', 'axis_direction_component', 'axis_origin_component', 'les_spec_name', 'rfg_number_of_modes', 'vm_number_of_vortices', 'vm_streamwise_fluct', 'vm_mass_conservation', 'volumetric_synthetic_turbulence_generator', 'volumetric_synthetic_turbulence_generator_option', 'volumetric_synthetic_turbulence_generator_option_thickness', 'prevent_reverse_flow', 'ke_spec', 'nut', 'kl', 'intermit', 'k', 'e', 'o', 'v2', 'turb_intensity', 'turb_length_scale', 'turb_hydraulic_diam', 'turb_viscosity_ratio', 'turb_viscosity_ratio_profile', 'rst_spec', 'uu', 'vv', 'ww', 'uv', 'vw', 'uw', 'ksgs_spec', 'ksgs', 'sgs_turb_intensity', 'granular_temperature', 'iac', 'lsfun', 'volume_fraction', 'species_in_mole_fractions', 'mf', 'elec_potential_type', 'potential_value', 'dual_potential_type', 'dual_potential_value', 'x_displacement_type', 'x_displacement_value', 'y_displacement_type', 'y_displacement_value', 'z_displacement_type', 'z_displacement_value', 'prob_mode_1', 'prob_mode_2', 'prob_mode_3', 'equ_required', 'uds_bc', 'uds', 'pb_disc_bc', 'pb_disc', 'pb_qmom_bc', 'pb_qmom', 'pb_smm_bc', 'pb_smm', 'pb_dqmom_bc', 'pb_dqmom', 'radiation_bc', 'radial_direction_component', 'coll_dtheta', 'coll_dphi', 'band_q_irrad', 'band_q_irrad_diffuse', 'parallel_collimated_beam', 'solar_direction', 'solar_irradiation', 't_b_b_spec', 't_b_b', 'in_emiss', 'fmean', 'fvar', 'fmean2', 'fvar2', 'premixc', 'premixc_var', 'ecfm_sigma', 'inert', 'pollut_no', 'pollut_hcn', 'pollut_nh3', 'pollut_n2o', 'pollut_urea', 'pollut_hnco', 'pollut_nco', 'pollut_so2', 'pollut_h2s', 'pollut_so3', 'pollut_sh', 'pollut_so', 'pollut_soot', 'pollut_nuclei', 'pollut_ctar', 'pollut_hg', 'pollut_hgcl2', 'pollut_hcl', 'pollut_hgo', 'pollut_cl', 'pollut_cl2', 'pollut_hgcl', 'pollut_hocl', 'tss_scalar', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'fensapice_flow_bc_subtype', 'fensapice_drop_bccustom', 'fensapice_drop_lwc', 'fensapice_drop_dtemp', 'fensapice_drop_ddiam', 'fensapice_drop_dv', 'fensapice_drop_dx', 'fensapice_drop_dy', 'fensapice_drop_dz', 'fensapice_dpm_surface_injection', 'fensapice_dpm_inj_nstream', 'fensapice_drop_icc', 'fensapice_drop_ctemp', 'fensapice_drop_cdiam', 'fensapice_drop_cv', 'fensapice_drop_cx', 'fensapice_drop_cy', 'fensapice_drop_cz', 'fensapice_drop_vrh', 'fensapice_drop_vrh_1', 'fensapice_drop_vc', 'mixing_plane_thread', 'wsf', 'wsb', 'wsn', 'solar_fluxes', 'solar_shining_factor', 'radiating_s2s_surface', 'ac_options', 'impedance_0', 'impedance_1', 'impedance_2', 'ac_wave', 'les_spec', 'b', 'strength']
    _child_classes = dict(
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        open_channel=open_channel,
        inlet_number=inlet_number,
        phase_spec=phase_spec,
        frame_of_reference=frame_of_reference,
        p0=p0,
        supersonic_or_initial_gauge_pressure=supersonic_or_initial_gauge_pressure,
        t0=t0,
        direction_spec=direction_spec,
        flow_spec=flow_spec,
        ht_local=ht_local,
        ht_total=ht_total,
        vmag=vmag,
        ht_bottom=ht_bottom,
        den_spec=den_spec,
        coordinate_system=coordinate_system,
        flow_direction_component=flow_direction_component,
        direction_vector_components=direction_vector_components,
        axis_direction_component=axis_direction_component_1,
        axis_origin_component=axis_origin_component_1,
        les_spec_name=les_spec_name,
        rfg_number_of_modes=rfg_number_of_modes,
        vm_number_of_vortices=vm_number_of_vortices,
        vm_streamwise_fluct=vm_streamwise_fluct,
        vm_mass_conservation=vm_mass_conservation,
        volumetric_synthetic_turbulence_generator=volumetric_synthetic_turbulence_generator,
        volumetric_synthetic_turbulence_generator_option=volumetric_synthetic_turbulence_generator_option,
        volumetric_synthetic_turbulence_generator_option_thickness=volumetric_synthetic_turbulence_generator_option_thickness,
        prevent_reverse_flow=prevent_reverse_flow,
        ke_spec=ke_spec,
        nut=nut,
        kl=kl,
        intermit=intermit,
        k=k,
        e=e,
        o=o,
        v2=v2,
        turb_intensity=turb_intensity,
        turb_length_scale=turb_length_scale,
        turb_hydraulic_diam=turb_hydraulic_diam,
        turb_viscosity_ratio=turb_viscosity_ratio,
        turb_viscosity_ratio_profile=turb_viscosity_ratio_profile,
        rst_spec=rst_spec,
        uu=uu,
        vv=vv,
        ww=ww,
        uv=uv,
        vw=vw,
        uw=uw,
        ksgs_spec=ksgs_spec,
        ksgs=ksgs,
        sgs_turb_intensity=sgs_turb_intensity,
        granular_temperature=granular_temperature,
        iac=iac,
        lsfun=lsfun,
        volume_fraction=volume_fraction,
        species_in_mole_fractions=species_in_mole_fractions,
        mf=mf,
        elec_potential_type=elec_potential_type,
        potential_value=potential_value,
        dual_potential_type=dual_potential_type,
        dual_potential_value=dual_potential_value,
        x_displacement_type=x_displacement_type,
        x_displacement_value=x_displacement_value,
        y_displacement_type=y_displacement_type,
        y_displacement_value=y_displacement_value,
        z_displacement_type=z_displacement_type,
        z_displacement_value=z_displacement_value,
        prob_mode_1=prob_mode_1,
        prob_mode_2=prob_mode_2,
        prob_mode_3=prob_mode_3,
        equ_required=equ_required,
        uds_bc=uds_bc,
        uds=uds,
        pb_disc_bc=pb_disc_bc,
        pb_disc=pb_disc,
        pb_qmom_bc=pb_qmom_bc,
        pb_qmom=pb_qmom,
        pb_smm_bc=pb_smm_bc,
        pb_smm=pb_smm,
        pb_dqmom_bc=pb_dqmom_bc,
        pb_dqmom=pb_dqmom,
        radiation_bc=radiation_bc,
        radial_direction_component=radial_direction_component,
        coll_dtheta=coll_dtheta,
        coll_dphi=coll_dphi,
        band_q_irrad=band_q_irrad,
        band_q_irrad_diffuse=band_q_irrad_diffuse,
        parallel_collimated_beam=parallel_collimated_beam,
        solar_direction=solar_direction,
        solar_irradiation=solar_irradiation,
        t_b_b_spec=t_b_b_spec,
        t_b_b=t_b_b,
        in_emiss=in_emiss,
        fmean=fmean,
        fvar=fvar,
        fmean2=fmean2,
        fvar2=fvar2,
        premixc=premixc,
        premixc_var=premixc_var,
        ecfm_sigma=ecfm_sigma,
        inert=inert,
        pollut_no=pollut_no,
        pollut_hcn=pollut_hcn,
        pollut_nh3=pollut_nh3,
        pollut_n2o=pollut_n2o,
        pollut_urea=pollut_urea,
        pollut_hnco=pollut_hnco,
        pollut_nco=pollut_nco,
        pollut_so2=pollut_so2,
        pollut_h2s=pollut_h2s,
        pollut_so3=pollut_so3,
        pollut_sh=pollut_sh,
        pollut_so=pollut_so,
        pollut_soot=pollut_soot,
        pollut_nuclei=pollut_nuclei,
        pollut_ctar=pollut_ctar,
        pollut_hg=pollut_hg,
        pollut_hgcl2=pollut_hgcl2,
        pollut_hcl=pollut_hcl,
        pollut_hgo=pollut_hgo,
        pollut_cl=pollut_cl,
        pollut_cl2=pollut_cl2,
        pollut_hgcl=pollut_hgcl,
        pollut_hocl=pollut_hocl,
        tss_scalar=tss_scalar,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        fensapice_flow_bc_subtype=fensapice_flow_bc_subtype,
        fensapice_drop_bccustom=fensapice_drop_bccustom,
        fensapice_drop_lwc=fensapice_drop_lwc,
        fensapice_drop_dtemp=fensapice_drop_dtemp,
        fensapice_drop_ddiam=fensapice_drop_ddiam,
        fensapice_drop_dv=fensapice_drop_dv,
        fensapice_drop_dx=fensapice_drop_dx,
        fensapice_drop_dy=fensapice_drop_dy,
        fensapice_drop_dz=fensapice_drop_dz,
        fensapice_dpm_surface_injection=fensapice_dpm_surface_injection,
        fensapice_dpm_inj_nstream=fensapice_dpm_inj_nstream,
        fensapice_drop_icc=fensapice_drop_icc,
        fensapice_drop_ctemp=fensapice_drop_ctemp,
        fensapice_drop_cdiam=fensapice_drop_cdiam,
        fensapice_drop_cv=fensapice_drop_cv,
        fensapice_drop_cx=fensapice_drop_cx,
        fensapice_drop_cy=fensapice_drop_cy,
        fensapice_drop_cz=fensapice_drop_cz,
        fensapice_drop_vrh=fensapice_drop_vrh,
        fensapice_drop_vrh_1=fensapice_drop_vrh_1,
        fensapice_drop_vc=fensapice_drop_vc,
        mixing_plane_thread=mixing_plane_thread,
        wsf=wsf,
        wsb=wsb,
        wsn=wsn,
        solar_fluxes=solar_fluxes,
        solar_shining_factor=solar_shining_factor,
        radiating_s2s_surface=radiating_s2s_surface,
        ac_options=ac_options,
        impedance_0=impedance_0,
        impedance_1=impedance_1,
        impedance_2=impedance_2,
        ac_wave=ac_wave,
        les_spec=les_spec,
        b=b,
        strength=strength,
    )
    return_type = 'object'

class phase_5(NamedObject[phase_5_child], CreatableNamedObjectMixinOld[phase_5_child]):
    """
    'phase' child.
    """
    _version = '222'
    fluent_name = 'phase'
    _python_name = 'phase'
    child_object_type = phase_5_child
    return_type = 'object'

class inlet_vent_child(Group):
    """
    'child_object_type' of inlet_vent.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'inlet_vent_child'
    child_names = ['phase', 'geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'open_channel', 'inlet_number', 'phase_spec', 'frame_of_reference', 'p0', 'supersonic_or_initial_gauge_pressure', 't0', 'direction_spec', 'flow_spec', 'ht_local', 'ht_total', 'vmag', 'ht_bottom', 'den_spec', 'coordinate_system', 'flow_direction_component', 'direction_vector_components', 'axis_direction_component', 'axis_origin_component', 'les_spec_name', 'rfg_number_of_modes', 'vm_number_of_vortices', 'vm_streamwise_fluct', 'vm_mass_conservation', 'volumetric_synthetic_turbulence_generator', 'volumetric_synthetic_turbulence_generator_option', 'volumetric_synthetic_turbulence_generator_option_thickness', 'prevent_reverse_flow', 'ke_spec', 'nut', 'kl', 'intermit', 'k', 'e', 'o', 'v2', 'turb_intensity', 'turb_length_scale', 'turb_hydraulic_diam', 'turb_viscosity_ratio', 'turb_viscosity_ratio_profile', 'rst_spec', 'uu', 'vv', 'ww', 'uv', 'vw', 'uw', 'ksgs_spec', 'ksgs', 'sgs_turb_intensity', 'granular_temperature', 'iac', 'lsfun', 'volume_fraction', 'species_in_mole_fractions', 'mf', 'elec_potential_type', 'potential_value', 'dual_potential_type', 'dual_potential_value', 'x_displacement_type', 'x_displacement_value', 'y_displacement_type', 'y_displacement_value', 'z_displacement_type', 'z_displacement_value', 'prob_mode_1', 'prob_mode_2', 'prob_mode_3', 'equ_required', 'uds_bc', 'uds', 'pb_disc_bc', 'pb_disc', 'pb_qmom_bc', 'pb_qmom', 'pb_smm_bc', 'pb_smm', 'pb_dqmom_bc', 'pb_dqmom', 'radiation_bc', 'radial_direction_component', 'coll_dtheta', 'coll_dphi', 'band_q_irrad', 'band_q_irrad_diffuse', 'parallel_collimated_beam', 'solar_direction', 'solar_irradiation', 't_b_b_spec', 't_b_b', 'in_emiss', 'fmean', 'fvar', 'fmean2', 'fvar2', 'premixc', 'premixc_var', 'ecfm_sigma', 'inert', 'pollut_no', 'pollut_hcn', 'pollut_nh3', 'pollut_n2o', 'pollut_urea', 'pollut_hnco', 'pollut_nco', 'pollut_so2', 'pollut_h2s', 'pollut_so3', 'pollut_sh', 'pollut_so', 'pollut_soot', 'pollut_nuclei', 'pollut_ctar', 'pollut_hg', 'pollut_hgcl2', 'pollut_hcl', 'pollut_hgo', 'pollut_cl', 'pollut_cl2', 'pollut_hgcl', 'pollut_hocl', 'tss_scalar', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'fensapice_flow_bc_subtype', 'fensapice_drop_bccustom', 'fensapice_drop_lwc', 'fensapice_drop_dtemp', 'fensapice_drop_ddiam', 'fensapice_drop_dv', 'fensapice_drop_dx', 'fensapice_drop_dy', 'fensapice_drop_dz', 'fensapice_dpm_surface_injection', 'fensapice_dpm_inj_nstream', 'fensapice_drop_icc', 'fensapice_drop_ctemp', 'fensapice_drop_cdiam', 'fensapice_drop_cv', 'fensapice_drop_cx', 'fensapice_drop_cy', 'fensapice_drop_cz', 'fensapice_drop_vrh', 'fensapice_drop_vrh_1', 'fensapice_drop_vc', 'mixing_plane_thread', 'wsf', 'wsb', 'wsn', 'solar_fluxes', 'solar_shining_factor', 'radiating_s2s_surface', 'ac_options', 'impedance_0', 'impedance_1', 'impedance_2', 'ac_wave', 'les_spec', 'b', 'strength']
    _child_classes = dict(
        phase=phase_5,
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        open_channel=open_channel,
        inlet_number=inlet_number,
        phase_spec=phase_spec,
        frame_of_reference=frame_of_reference,
        p0=p0,
        supersonic_or_initial_gauge_pressure=supersonic_or_initial_gauge_pressure,
        t0=t0,
        direction_spec=direction_spec,
        flow_spec=flow_spec,
        ht_local=ht_local,
        ht_total=ht_total,
        vmag=vmag,
        ht_bottom=ht_bottom,
        den_spec=den_spec,
        coordinate_system=coordinate_system,
        flow_direction_component=flow_direction_component,
        direction_vector_components=direction_vector_components,
        axis_direction_component=axis_direction_component_1,
        axis_origin_component=axis_origin_component_1,
        les_spec_name=les_spec_name,
        rfg_number_of_modes=rfg_number_of_modes,
        vm_number_of_vortices=vm_number_of_vortices,
        vm_streamwise_fluct=vm_streamwise_fluct,
        vm_mass_conservation=vm_mass_conservation,
        volumetric_synthetic_turbulence_generator=volumetric_synthetic_turbulence_generator,
        volumetric_synthetic_turbulence_generator_option=volumetric_synthetic_turbulence_generator_option,
        volumetric_synthetic_turbulence_generator_option_thickness=volumetric_synthetic_turbulence_generator_option_thickness,
        prevent_reverse_flow=prevent_reverse_flow,
        ke_spec=ke_spec,
        nut=nut,
        kl=kl,
        intermit=intermit,
        k=k,
        e=e,
        o=o,
        v2=v2,
        turb_intensity=turb_intensity,
        turb_length_scale=turb_length_scale,
        turb_hydraulic_diam=turb_hydraulic_diam,
        turb_viscosity_ratio=turb_viscosity_ratio,
        turb_viscosity_ratio_profile=turb_viscosity_ratio_profile,
        rst_spec=rst_spec,
        uu=uu,
        vv=vv,
        ww=ww,
        uv=uv,
        vw=vw,
        uw=uw,
        ksgs_spec=ksgs_spec,
        ksgs=ksgs,
        sgs_turb_intensity=sgs_turb_intensity,
        granular_temperature=granular_temperature,
        iac=iac,
        lsfun=lsfun,
        volume_fraction=volume_fraction,
        species_in_mole_fractions=species_in_mole_fractions,
        mf=mf,
        elec_potential_type=elec_potential_type,
        potential_value=potential_value,
        dual_potential_type=dual_potential_type,
        dual_potential_value=dual_potential_value,
        x_displacement_type=x_displacement_type,
        x_displacement_value=x_displacement_value,
        y_displacement_type=y_displacement_type,
        y_displacement_value=y_displacement_value,
        z_displacement_type=z_displacement_type,
        z_displacement_value=z_displacement_value,
        prob_mode_1=prob_mode_1,
        prob_mode_2=prob_mode_2,
        prob_mode_3=prob_mode_3,
        equ_required=equ_required,
        uds_bc=uds_bc,
        uds=uds,
        pb_disc_bc=pb_disc_bc,
        pb_disc=pb_disc,
        pb_qmom_bc=pb_qmom_bc,
        pb_qmom=pb_qmom,
        pb_smm_bc=pb_smm_bc,
        pb_smm=pb_smm,
        pb_dqmom_bc=pb_dqmom_bc,
        pb_dqmom=pb_dqmom,
        radiation_bc=radiation_bc,
        radial_direction_component=radial_direction_component,
        coll_dtheta=coll_dtheta,
        coll_dphi=coll_dphi,
        band_q_irrad=band_q_irrad,
        band_q_irrad_diffuse=band_q_irrad_diffuse,
        parallel_collimated_beam=parallel_collimated_beam,
        solar_direction=solar_direction,
        solar_irradiation=solar_irradiation,
        t_b_b_spec=t_b_b_spec,
        t_b_b=t_b_b,
        in_emiss=in_emiss,
        fmean=fmean,
        fvar=fvar,
        fmean2=fmean2,
        fvar2=fvar2,
        premixc=premixc,
        premixc_var=premixc_var,
        ecfm_sigma=ecfm_sigma,
        inert=inert,
        pollut_no=pollut_no,
        pollut_hcn=pollut_hcn,
        pollut_nh3=pollut_nh3,
        pollut_n2o=pollut_n2o,
        pollut_urea=pollut_urea,
        pollut_hnco=pollut_hnco,
        pollut_nco=pollut_nco,
        pollut_so2=pollut_so2,
        pollut_h2s=pollut_h2s,
        pollut_so3=pollut_so3,
        pollut_sh=pollut_sh,
        pollut_so=pollut_so,
        pollut_soot=pollut_soot,
        pollut_nuclei=pollut_nuclei,
        pollut_ctar=pollut_ctar,
        pollut_hg=pollut_hg,
        pollut_hgcl2=pollut_hgcl2,
        pollut_hcl=pollut_hcl,
        pollut_hgo=pollut_hgo,
        pollut_cl=pollut_cl,
        pollut_cl2=pollut_cl2,
        pollut_hgcl=pollut_hgcl,
        pollut_hocl=pollut_hocl,
        tss_scalar=tss_scalar,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        fensapice_flow_bc_subtype=fensapice_flow_bc_subtype,
        fensapice_drop_bccustom=fensapice_drop_bccustom,
        fensapice_drop_lwc=fensapice_drop_lwc,
        fensapice_drop_dtemp=fensapice_drop_dtemp,
        fensapice_drop_ddiam=fensapice_drop_ddiam,
        fensapice_drop_dv=fensapice_drop_dv,
        fensapice_drop_dx=fensapice_drop_dx,
        fensapice_drop_dy=fensapice_drop_dy,
        fensapice_drop_dz=fensapice_drop_dz,
        fensapice_dpm_surface_injection=fensapice_dpm_surface_injection,
        fensapice_dpm_inj_nstream=fensapice_dpm_inj_nstream,
        fensapice_drop_icc=fensapice_drop_icc,
        fensapice_drop_ctemp=fensapice_drop_ctemp,
        fensapice_drop_cdiam=fensapice_drop_cdiam,
        fensapice_drop_cv=fensapice_drop_cv,
        fensapice_drop_cx=fensapice_drop_cx,
        fensapice_drop_cy=fensapice_drop_cy,
        fensapice_drop_cz=fensapice_drop_cz,
        fensapice_drop_vrh=fensapice_drop_vrh,
        fensapice_drop_vrh_1=fensapice_drop_vrh_1,
        fensapice_drop_vc=fensapice_drop_vc,
        mixing_plane_thread=mixing_plane_thread,
        wsf=wsf,
        wsb=wsb,
        wsn=wsn,
        solar_fluxes=solar_fluxes,
        solar_shining_factor=solar_shining_factor,
        radiating_s2s_surface=radiating_s2s_surface,
        ac_options=ac_options,
        impedance_0=impedance_0,
        impedance_1=impedance_1,
        impedance_2=impedance_2,
        ac_wave=ac_wave,
        les_spec=les_spec,
        b=b,
        strength=strength,
    )
    return_type = 'object'

class inlet_vent(NamedObject[inlet_vent_child], CreatableNamedObjectMixinOld[inlet_vent_child]):
    """
    'inlet_vent' child.
    """
    _version = '222'
    fluent_name = 'inlet-vent'
    _python_name = 'inlet_vent'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = inlet_vent_child
    return_type = 'object'

class fan_omega(Real, AllowedValuesMixin):
    """
    'fan_omega' child.
    """
    _version = '222'
    fluent_name = 'fan-omega'
    _python_name = 'fan_omega'
    return_type = 'object'

class fan_origin_components_child(Real, AllowedValuesMixin):
    """
    'child_object_type' of fan_origin_components.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'fan_origin_components_child'
    return_type = 'object'

class fan_origin_components(ListObject[fan_origin_components_child]):
    """
    'fan_origin_components' child.
    """
    _version = '222'
    fluent_name = 'fan-origin-components'
    _python_name = 'fan_origin_components'
    child_object_type = fan_origin_components_child
    return_type = 'object'

class phase_6_child(Group):
    """
    'child_object_type' of phase.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'phase_child'
    child_names = ['geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'open_channel', 'inlet_number', 'phase_spec', 'frame_of_reference', 'p0', 'supersonic_or_initial_gauge_pressure', 't0', 'direction_spec', 'flow_spec', 'ht_local', 'ht_total', 'vmag', 'ht_bottom', 'den_spec', 'coordinate_system', 'flow_direction_component', 'direction_vector_components', 'axis_direction_component', 'axis_origin_component', 'les_spec_name', 'rfg_number_of_modes', 'vm_number_of_vortices', 'vm_streamwise_fluct', 'vm_mass_conservation', 'volumetric_synthetic_turbulence_generator', 'volumetric_synthetic_turbulence_generator_option', 'volumetric_synthetic_turbulence_generator_option_thickness', 'prevent_reverse_flow', 'ke_spec', 'nut', 'kl', 'intermit', 'k', 'e', 'o', 'v2', 'turb_intensity', 'turb_length_scale', 'turb_hydraulic_diam', 'turb_viscosity_ratio', 'turb_viscosity_ratio_profile', 'rst_spec', 'uu', 'vv', 'ww', 'uv', 'vw', 'uw', 'ksgs_spec', 'ksgs', 'sgs_turb_intensity', 'granular_temperature', 'iac', 'lsfun', 'volume_fraction', 'species_in_mole_fractions', 'mf', 'elec_potential_type', 'potential_value', 'dual_potential_type', 'dual_potential_value', 'x_displacement_type', 'x_displacement_value', 'y_displacement_type', 'y_displacement_value', 'z_displacement_type', 'z_displacement_value', 'prob_mode_1', 'prob_mode_2', 'prob_mode_3', 'equ_required', 'uds_bc', 'uds', 'pb_disc_bc', 'pb_disc', 'pb_qmom_bc', 'pb_qmom', 'pb_smm_bc', 'pb_smm', 'pb_dqmom_bc', 'pb_dqmom', 'radiation_bc', 'radial_direction_component', 'coll_dtheta', 'coll_dphi', 'band_q_irrad', 'band_q_irrad_diffuse', 'parallel_collimated_beam', 'solar_direction', 'solar_irradiation', 't_b_b_spec', 't_b_b', 'in_emiss', 'fmean', 'fvar', 'fmean2', 'fvar2', 'premixc', 'premixc_var', 'ecfm_sigma', 'inert', 'pollut_no', 'pollut_hcn', 'pollut_nh3', 'pollut_n2o', 'pollut_urea', 'pollut_hnco', 'pollut_nco', 'pollut_so2', 'pollut_h2s', 'pollut_so3', 'pollut_sh', 'pollut_so', 'pollut_soot', 'pollut_nuclei', 'pollut_ctar', 'pollut_hg', 'pollut_hgcl2', 'pollut_hcl', 'pollut_hgo', 'pollut_cl', 'pollut_cl2', 'pollut_hgcl', 'pollut_hocl', 'tss_scalar', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'fensapice_flow_bc_subtype', 'fensapice_drop_bccustom', 'fensapice_drop_lwc', 'fensapice_drop_dtemp', 'fensapice_drop_ddiam', 'fensapice_drop_dv', 'fensapice_drop_dx', 'fensapice_drop_dy', 'fensapice_drop_dz', 'fensapice_dpm_surface_injection', 'fensapice_dpm_inj_nstream', 'fensapice_drop_icc', 'fensapice_drop_ctemp', 'fensapice_drop_cdiam', 'fensapice_drop_cv', 'fensapice_drop_cx', 'fensapice_drop_cy', 'fensapice_drop_cz', 'fensapice_drop_vrh', 'fensapice_drop_vrh_1', 'fensapice_drop_vc', 'mixing_plane_thread', 'wsf', 'wsb', 'wsn', 'solar_fluxes', 'solar_shining_factor', 'radiating_s2s_surface', 'ac_options', 'impedance_0', 'impedance_1', 'impedance_2', 'ac_wave', 'les_spec', 'a', 'swirl_model', 'swirl_factor', 'fan_omega', 'fan_origin_components', 'strength', 'new_fan_definition']
    _child_classes = dict(
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        open_channel=open_channel,
        inlet_number=inlet_number,
        phase_spec=phase_spec,
        frame_of_reference=frame_of_reference,
        p0=p0,
        supersonic_or_initial_gauge_pressure=supersonic_or_initial_gauge_pressure,
        t0=t0,
        direction_spec=direction_spec,
        flow_spec=flow_spec,
        ht_local=ht_local,
        ht_total=ht_total,
        vmag=vmag,
        ht_bottom=ht_bottom,
        den_spec=den_spec,
        coordinate_system=coordinate_system,
        flow_direction_component=flow_direction_component,
        direction_vector_components=direction_vector_components,
        axis_direction_component=axis_direction_component_1,
        axis_origin_component=axis_origin_component_1,
        les_spec_name=les_spec_name,
        rfg_number_of_modes=rfg_number_of_modes,
        vm_number_of_vortices=vm_number_of_vortices,
        vm_streamwise_fluct=vm_streamwise_fluct,
        vm_mass_conservation=vm_mass_conservation,
        volumetric_synthetic_turbulence_generator=volumetric_synthetic_turbulence_generator,
        volumetric_synthetic_turbulence_generator_option=volumetric_synthetic_turbulence_generator_option,
        volumetric_synthetic_turbulence_generator_option_thickness=volumetric_synthetic_turbulence_generator_option_thickness,
        prevent_reverse_flow=prevent_reverse_flow,
        ke_spec=ke_spec,
        nut=nut,
        kl=kl,
        intermit=intermit,
        k=k,
        e=e,
        o=o,
        v2=v2,
        turb_intensity=turb_intensity,
        turb_length_scale=turb_length_scale,
        turb_hydraulic_diam=turb_hydraulic_diam,
        turb_viscosity_ratio=turb_viscosity_ratio,
        turb_viscosity_ratio_profile=turb_viscosity_ratio_profile,
        rst_spec=rst_spec,
        uu=uu,
        vv=vv,
        ww=ww,
        uv=uv,
        vw=vw,
        uw=uw,
        ksgs_spec=ksgs_spec,
        ksgs=ksgs,
        sgs_turb_intensity=sgs_turb_intensity,
        granular_temperature=granular_temperature,
        iac=iac,
        lsfun=lsfun,
        volume_fraction=volume_fraction,
        species_in_mole_fractions=species_in_mole_fractions,
        mf=mf,
        elec_potential_type=elec_potential_type,
        potential_value=potential_value,
        dual_potential_type=dual_potential_type,
        dual_potential_value=dual_potential_value,
        x_displacement_type=x_displacement_type,
        x_displacement_value=x_displacement_value,
        y_displacement_type=y_displacement_type,
        y_displacement_value=y_displacement_value,
        z_displacement_type=z_displacement_type,
        z_displacement_value=z_displacement_value,
        prob_mode_1=prob_mode_1,
        prob_mode_2=prob_mode_2,
        prob_mode_3=prob_mode_3,
        equ_required=equ_required,
        uds_bc=uds_bc,
        uds=uds,
        pb_disc_bc=pb_disc_bc,
        pb_disc=pb_disc,
        pb_qmom_bc=pb_qmom_bc,
        pb_qmom=pb_qmom,
        pb_smm_bc=pb_smm_bc,
        pb_smm=pb_smm,
        pb_dqmom_bc=pb_dqmom_bc,
        pb_dqmom=pb_dqmom,
        radiation_bc=radiation_bc,
        radial_direction_component=radial_direction_component,
        coll_dtheta=coll_dtheta,
        coll_dphi=coll_dphi,
        band_q_irrad=band_q_irrad,
        band_q_irrad_diffuse=band_q_irrad_diffuse,
        parallel_collimated_beam=parallel_collimated_beam,
        solar_direction=solar_direction,
        solar_irradiation=solar_irradiation,
        t_b_b_spec=t_b_b_spec,
        t_b_b=t_b_b,
        in_emiss=in_emiss,
        fmean=fmean,
        fvar=fvar,
        fmean2=fmean2,
        fvar2=fvar2,
        premixc=premixc,
        premixc_var=premixc_var,
        ecfm_sigma=ecfm_sigma,
        inert=inert,
        pollut_no=pollut_no,
        pollut_hcn=pollut_hcn,
        pollut_nh3=pollut_nh3,
        pollut_n2o=pollut_n2o,
        pollut_urea=pollut_urea,
        pollut_hnco=pollut_hnco,
        pollut_nco=pollut_nco,
        pollut_so2=pollut_so2,
        pollut_h2s=pollut_h2s,
        pollut_so3=pollut_so3,
        pollut_sh=pollut_sh,
        pollut_so=pollut_so,
        pollut_soot=pollut_soot,
        pollut_nuclei=pollut_nuclei,
        pollut_ctar=pollut_ctar,
        pollut_hg=pollut_hg,
        pollut_hgcl2=pollut_hgcl2,
        pollut_hcl=pollut_hcl,
        pollut_hgo=pollut_hgo,
        pollut_cl=pollut_cl,
        pollut_cl2=pollut_cl2,
        pollut_hgcl=pollut_hgcl,
        pollut_hocl=pollut_hocl,
        tss_scalar=tss_scalar,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        fensapice_flow_bc_subtype=fensapice_flow_bc_subtype,
        fensapice_drop_bccustom=fensapice_drop_bccustom,
        fensapice_drop_lwc=fensapice_drop_lwc,
        fensapice_drop_dtemp=fensapice_drop_dtemp,
        fensapice_drop_ddiam=fensapice_drop_ddiam,
        fensapice_drop_dv=fensapice_drop_dv,
        fensapice_drop_dx=fensapice_drop_dx,
        fensapice_drop_dy=fensapice_drop_dy,
        fensapice_drop_dz=fensapice_drop_dz,
        fensapice_dpm_surface_injection=fensapice_dpm_surface_injection,
        fensapice_dpm_inj_nstream=fensapice_dpm_inj_nstream,
        fensapice_drop_icc=fensapice_drop_icc,
        fensapice_drop_ctemp=fensapice_drop_ctemp,
        fensapice_drop_cdiam=fensapice_drop_cdiam,
        fensapice_drop_cv=fensapice_drop_cv,
        fensapice_drop_cx=fensapice_drop_cx,
        fensapice_drop_cy=fensapice_drop_cy,
        fensapice_drop_cz=fensapice_drop_cz,
        fensapice_drop_vrh=fensapice_drop_vrh,
        fensapice_drop_vrh_1=fensapice_drop_vrh_1,
        fensapice_drop_vc=fensapice_drop_vc,
        mixing_plane_thread=mixing_plane_thread,
        wsf=wsf,
        wsb=wsb,
        wsn=wsn,
        solar_fluxes=solar_fluxes,
        solar_shining_factor=solar_shining_factor,
        radiating_s2s_surface=radiating_s2s_surface,
        ac_options=ac_options,
        impedance_0=impedance_0,
        impedance_1=impedance_1,
        impedance_2=impedance_2,
        ac_wave=ac_wave,
        les_spec=les_spec,
        a=a,
        swirl_model=swirl_model,
        swirl_factor=swirl_factor,
        fan_omega=fan_omega,
        fan_origin_components=fan_origin_components,
        strength=strength,
        new_fan_definition=new_fan_definition,
    )
    return_type = 'object'

class phase_6(NamedObject[phase_6_child], CreatableNamedObjectMixinOld[phase_6_child]):
    """
    'phase' child.
    """
    _version = '222'
    fluent_name = 'phase'
    _python_name = 'phase'
    child_object_type = phase_6_child
    return_type = 'object'

class intake_fan_child(Group):
    """
    'child_object_type' of intake_fan.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'intake_fan_child'
    child_names = ['phase', 'geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'open_channel', 'inlet_number', 'phase_spec', 'frame_of_reference', 'p0', 'supersonic_or_initial_gauge_pressure', 't0', 'direction_spec', 'flow_spec', 'ht_local', 'ht_total', 'vmag', 'ht_bottom', 'den_spec', 'coordinate_system', 'flow_direction_component', 'direction_vector_components', 'axis_direction_component', 'axis_origin_component', 'les_spec_name', 'rfg_number_of_modes', 'vm_number_of_vortices', 'vm_streamwise_fluct', 'vm_mass_conservation', 'volumetric_synthetic_turbulence_generator', 'volumetric_synthetic_turbulence_generator_option', 'volumetric_synthetic_turbulence_generator_option_thickness', 'prevent_reverse_flow', 'ke_spec', 'nut', 'kl', 'intermit', 'k', 'e', 'o', 'v2', 'turb_intensity', 'turb_length_scale', 'turb_hydraulic_diam', 'turb_viscosity_ratio', 'turb_viscosity_ratio_profile', 'rst_spec', 'uu', 'vv', 'ww', 'uv', 'vw', 'uw', 'ksgs_spec', 'ksgs', 'sgs_turb_intensity', 'granular_temperature', 'iac', 'lsfun', 'volume_fraction', 'species_in_mole_fractions', 'mf', 'elec_potential_type', 'potential_value', 'dual_potential_type', 'dual_potential_value', 'x_displacement_type', 'x_displacement_value', 'y_displacement_type', 'y_displacement_value', 'z_displacement_type', 'z_displacement_value', 'prob_mode_1', 'prob_mode_2', 'prob_mode_3', 'equ_required', 'uds_bc', 'uds', 'pb_disc_bc', 'pb_disc', 'pb_qmom_bc', 'pb_qmom', 'pb_smm_bc', 'pb_smm', 'pb_dqmom_bc', 'pb_dqmom', 'radiation_bc', 'radial_direction_component', 'coll_dtheta', 'coll_dphi', 'band_q_irrad', 'band_q_irrad_diffuse', 'parallel_collimated_beam', 'solar_direction', 'solar_irradiation', 't_b_b_spec', 't_b_b', 'in_emiss', 'fmean', 'fvar', 'fmean2', 'fvar2', 'premixc', 'premixc_var', 'ecfm_sigma', 'inert', 'pollut_no', 'pollut_hcn', 'pollut_nh3', 'pollut_n2o', 'pollut_urea', 'pollut_hnco', 'pollut_nco', 'pollut_so2', 'pollut_h2s', 'pollut_so3', 'pollut_sh', 'pollut_so', 'pollut_soot', 'pollut_nuclei', 'pollut_ctar', 'pollut_hg', 'pollut_hgcl2', 'pollut_hcl', 'pollut_hgo', 'pollut_cl', 'pollut_cl2', 'pollut_hgcl', 'pollut_hocl', 'tss_scalar', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'fensapice_flow_bc_subtype', 'fensapice_drop_bccustom', 'fensapice_drop_lwc', 'fensapice_drop_dtemp', 'fensapice_drop_ddiam', 'fensapice_drop_dv', 'fensapice_drop_dx', 'fensapice_drop_dy', 'fensapice_drop_dz', 'fensapice_dpm_surface_injection', 'fensapice_dpm_inj_nstream', 'fensapice_drop_icc', 'fensapice_drop_ctemp', 'fensapice_drop_cdiam', 'fensapice_drop_cv', 'fensapice_drop_cx', 'fensapice_drop_cy', 'fensapice_drop_cz', 'fensapice_drop_vrh', 'fensapice_drop_vrh_1', 'fensapice_drop_vc', 'mixing_plane_thread', 'wsf', 'wsb', 'wsn', 'solar_fluxes', 'solar_shining_factor', 'radiating_s2s_surface', 'ac_options', 'impedance_0', 'impedance_1', 'impedance_2', 'ac_wave', 'les_spec', 'a', 'swirl_model', 'swirl_factor', 'fan_omega', 'fan_origin_components', 'strength', 'new_fan_definition']
    _child_classes = dict(
        phase=phase_6,
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        open_channel=open_channel,
        inlet_number=inlet_number,
        phase_spec=phase_spec,
        frame_of_reference=frame_of_reference,
        p0=p0,
        supersonic_or_initial_gauge_pressure=supersonic_or_initial_gauge_pressure,
        t0=t0,
        direction_spec=direction_spec,
        flow_spec=flow_spec,
        ht_local=ht_local,
        ht_total=ht_total,
        vmag=vmag,
        ht_bottom=ht_bottom,
        den_spec=den_spec,
        coordinate_system=coordinate_system,
        flow_direction_component=flow_direction_component,
        direction_vector_components=direction_vector_components,
        axis_direction_component=axis_direction_component_1,
        axis_origin_component=axis_origin_component_1,
        les_spec_name=les_spec_name,
        rfg_number_of_modes=rfg_number_of_modes,
        vm_number_of_vortices=vm_number_of_vortices,
        vm_streamwise_fluct=vm_streamwise_fluct,
        vm_mass_conservation=vm_mass_conservation,
        volumetric_synthetic_turbulence_generator=volumetric_synthetic_turbulence_generator,
        volumetric_synthetic_turbulence_generator_option=volumetric_synthetic_turbulence_generator_option,
        volumetric_synthetic_turbulence_generator_option_thickness=volumetric_synthetic_turbulence_generator_option_thickness,
        prevent_reverse_flow=prevent_reverse_flow,
        ke_spec=ke_spec,
        nut=nut,
        kl=kl,
        intermit=intermit,
        k=k,
        e=e,
        o=o,
        v2=v2,
        turb_intensity=turb_intensity,
        turb_length_scale=turb_length_scale,
        turb_hydraulic_diam=turb_hydraulic_diam,
        turb_viscosity_ratio=turb_viscosity_ratio,
        turb_viscosity_ratio_profile=turb_viscosity_ratio_profile,
        rst_spec=rst_spec,
        uu=uu,
        vv=vv,
        ww=ww,
        uv=uv,
        vw=vw,
        uw=uw,
        ksgs_spec=ksgs_spec,
        ksgs=ksgs,
        sgs_turb_intensity=sgs_turb_intensity,
        granular_temperature=granular_temperature,
        iac=iac,
        lsfun=lsfun,
        volume_fraction=volume_fraction,
        species_in_mole_fractions=species_in_mole_fractions,
        mf=mf,
        elec_potential_type=elec_potential_type,
        potential_value=potential_value,
        dual_potential_type=dual_potential_type,
        dual_potential_value=dual_potential_value,
        x_displacement_type=x_displacement_type,
        x_displacement_value=x_displacement_value,
        y_displacement_type=y_displacement_type,
        y_displacement_value=y_displacement_value,
        z_displacement_type=z_displacement_type,
        z_displacement_value=z_displacement_value,
        prob_mode_1=prob_mode_1,
        prob_mode_2=prob_mode_2,
        prob_mode_3=prob_mode_3,
        equ_required=equ_required,
        uds_bc=uds_bc,
        uds=uds,
        pb_disc_bc=pb_disc_bc,
        pb_disc=pb_disc,
        pb_qmom_bc=pb_qmom_bc,
        pb_qmom=pb_qmom,
        pb_smm_bc=pb_smm_bc,
        pb_smm=pb_smm,
        pb_dqmom_bc=pb_dqmom_bc,
        pb_dqmom=pb_dqmom,
        radiation_bc=radiation_bc,
        radial_direction_component=radial_direction_component,
        coll_dtheta=coll_dtheta,
        coll_dphi=coll_dphi,
        band_q_irrad=band_q_irrad,
        band_q_irrad_diffuse=band_q_irrad_diffuse,
        parallel_collimated_beam=parallel_collimated_beam,
        solar_direction=solar_direction,
        solar_irradiation=solar_irradiation,
        t_b_b_spec=t_b_b_spec,
        t_b_b=t_b_b,
        in_emiss=in_emiss,
        fmean=fmean,
        fvar=fvar,
        fmean2=fmean2,
        fvar2=fvar2,
        premixc=premixc,
        premixc_var=premixc_var,
        ecfm_sigma=ecfm_sigma,
        inert=inert,
        pollut_no=pollut_no,
        pollut_hcn=pollut_hcn,
        pollut_nh3=pollut_nh3,
        pollut_n2o=pollut_n2o,
        pollut_urea=pollut_urea,
        pollut_hnco=pollut_hnco,
        pollut_nco=pollut_nco,
        pollut_so2=pollut_so2,
        pollut_h2s=pollut_h2s,
        pollut_so3=pollut_so3,
        pollut_sh=pollut_sh,
        pollut_so=pollut_so,
        pollut_soot=pollut_soot,
        pollut_nuclei=pollut_nuclei,
        pollut_ctar=pollut_ctar,
        pollut_hg=pollut_hg,
        pollut_hgcl2=pollut_hgcl2,
        pollut_hcl=pollut_hcl,
        pollut_hgo=pollut_hgo,
        pollut_cl=pollut_cl,
        pollut_cl2=pollut_cl2,
        pollut_hgcl=pollut_hgcl,
        pollut_hocl=pollut_hocl,
        tss_scalar=tss_scalar,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        fensapice_flow_bc_subtype=fensapice_flow_bc_subtype,
        fensapice_drop_bccustom=fensapice_drop_bccustom,
        fensapice_drop_lwc=fensapice_drop_lwc,
        fensapice_drop_dtemp=fensapice_drop_dtemp,
        fensapice_drop_ddiam=fensapice_drop_ddiam,
        fensapice_drop_dv=fensapice_drop_dv,
        fensapice_drop_dx=fensapice_drop_dx,
        fensapice_drop_dy=fensapice_drop_dy,
        fensapice_drop_dz=fensapice_drop_dz,
        fensapice_dpm_surface_injection=fensapice_dpm_surface_injection,
        fensapice_dpm_inj_nstream=fensapice_dpm_inj_nstream,
        fensapice_drop_icc=fensapice_drop_icc,
        fensapice_drop_ctemp=fensapice_drop_ctemp,
        fensapice_drop_cdiam=fensapice_drop_cdiam,
        fensapice_drop_cv=fensapice_drop_cv,
        fensapice_drop_cx=fensapice_drop_cx,
        fensapice_drop_cy=fensapice_drop_cy,
        fensapice_drop_cz=fensapice_drop_cz,
        fensapice_drop_vrh=fensapice_drop_vrh,
        fensapice_drop_vrh_1=fensapice_drop_vrh_1,
        fensapice_drop_vc=fensapice_drop_vc,
        mixing_plane_thread=mixing_plane_thread,
        wsf=wsf,
        wsb=wsb,
        wsn=wsn,
        solar_fluxes=solar_fluxes,
        solar_shining_factor=solar_shining_factor,
        radiating_s2s_surface=radiating_s2s_surface,
        ac_options=ac_options,
        impedance_0=impedance_0,
        impedance_1=impedance_1,
        impedance_2=impedance_2,
        ac_wave=ac_wave,
        les_spec=les_spec,
        a=a,
        swirl_model=swirl_model,
        swirl_factor=swirl_factor,
        fan_omega=fan_omega,
        fan_origin_components=fan_origin_components,
        strength=strength,
        new_fan_definition=new_fan_definition,
    )
    return_type = 'object'

class intake_fan(NamedObject[intake_fan_child], CreatableNamedObjectMixinOld[intake_fan_child]):
    """
    'intake_fan' child.
    """
    _version = '222'
    fluent_name = 'intake-fan'
    _python_name = 'intake_fan'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = intake_fan_child
    return_type = 'object'

class non_overlap_zone_name(String, AllowedValuesMixin):
    """
    'non_overlap_zone_name' child.
    """
    _version = '222'
    fluent_name = 'non-overlap-zone-name'
    _python_name = 'non_overlap_zone_name'
    return_type = 'object'

class phase_7_child(Group):
    """
    'child_object_type' of phase.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'phase_child'
    child_names = ['geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'non_overlap_zone_name']
    _child_classes = dict(
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        non_overlap_zone_name=non_overlap_zone_name,
    )
    return_type = 'object'

class phase_7(NamedObject[phase_7_child], CreatableNamedObjectMixinOld[phase_7_child]):
    """
    'phase' child.
    """
    _version = '222'
    fluent_name = 'phase'
    _python_name = 'phase'
    child_object_type = phase_7_child
    return_type = 'object'

class interface_child(Group):
    """
    'child_object_type' of interface.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'interface_child'
    child_names = ['phase', 'geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'non_overlap_zone_name']
    _child_classes = dict(
        phase=phase_7,
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        non_overlap_zone_name=non_overlap_zone_name,
    )
    return_type = 'object'

class interface(NamedObject[interface_child], CreatableNamedObjectMixinOld[interface_child]):
    """
    'interface' child.
    """
    _version = '222'
    fluent_name = 'interface'
    _python_name = 'interface'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = interface_child
    return_type = 'object'

class is_not_a_rans_les_interface(Boolean, AllowedValuesMixin):
    """
    'is_not_a_rans_les_interface' child.
    """
    _version = '222'
    fluent_name = 'is-not-a-rans-les-interface'
    _python_name = 'is_not_a_rans_les_interface'
    return_type = 'object'

class phase_8_child(Group):
    """
    'child_object_type' of phase.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'phase_child'
    child_names = ['is_not_a_rans_les_interface']
    _child_classes = dict(
        is_not_a_rans_les_interface=is_not_a_rans_les_interface,
    )
    return_type = 'object'

class phase_8(NamedObject[phase_8_child], CreatableNamedObjectMixinOld[phase_8_child]):
    """
    'phase' child.
    """
    _version = '222'
    fluent_name = 'phase'
    _python_name = 'phase'
    child_object_type = phase_8_child
    return_type = 'object'

class interior_child(Group):
    """
    'child_object_type' of interior.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'interior_child'
    child_names = ['phase', 'is_not_a_rans_les_interface']
    _child_classes = dict(
        phase=phase_8,
        is_not_a_rans_les_interface=is_not_a_rans_les_interface,
    )
    return_type = 'object'

class interior(NamedObject[interior_child], CreatableNamedObjectMixinOld[interior_child]):
    """
    'interior' child.
    """
    _version = '222'
    fluent_name = 'interior'
    _python_name = 'interior'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = interior_child
    return_type = 'object'

class mass_flow(Group):
    """
    'mass_flow' child.
    """
    _version = '222'
    fluent_name = 'mass-flow'
    _python_name = 'mass_flow'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class ec_mass_flow(Group):
    """
    'ec_mass_flow' child.
    """
    _version = '222'
    fluent_name = 'ec-mass-flow'
    _python_name = 'ec_mass_flow'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class mass_flux(Group):
    """
    'mass_flux' child.
    """
    _version = '222'
    fluent_name = 'mass-flux'
    _python_name = 'mass_flux'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class mass_flux_ave(Real, AllowedValuesMixin):
    """
    'mass_flux_ave' child.
    """
    _version = '222'
    fluent_name = 'mass-flux-ave'
    _python_name = 'mass_flux_ave'
    return_type = 'object'

class tref(Real, AllowedValuesMixin):
    """
    'tref' child.
    """
    _version = '222'
    fluent_name = 'tref'
    _python_name = 'tref'
    return_type = 'object'

class pref(Real, AllowedValuesMixin):
    """
    'pref' child.
    """
    _version = '222'
    fluent_name = 'pref'
    _python_name = 'pref'
    return_type = 'object'

class upstream_torque(Real, AllowedValuesMixin):
    """
    'upstream_torque' child.
    """
    _version = '222'
    fluent_name = 'upstream-torque'
    _python_name = 'upstream_torque'
    return_type = 'object'

class upstream_t_enthalpy(Real, AllowedValuesMixin):
    """
    'upstream_t_enthalpy' child.
    """
    _version = '222'
    fluent_name = 'upstream-t-enthalpy'
    _python_name = 'upstream_t_enthalpy'
    return_type = 'object'

class x_fan_origin(Real, AllowedValuesMixin):
    """
    'x_fan_origin' child.
    """
    _version = '222'
    fluent_name = 'x-fan-origin'
    _python_name = 'x_fan_origin'
    return_type = 'object'

class y_fan_origin(Real, AllowedValuesMixin):
    """
    'y_fan_origin' child.
    """
    _version = '222'
    fluent_name = 'y-fan-origin'
    _python_name = 'y_fan_origin'
    return_type = 'object'

class z_fan_origin(Real, AllowedValuesMixin):
    """
    'z_fan_origin' child.
    """
    _version = '222'
    fluent_name = 'z-fan-origin'
    _python_name = 'z_fan_origin'
    return_type = 'object'

class slip_velocity(String, AllowedValuesMixin):
    """
    'slip_velocity' child.
    """
    _version = '222'
    fluent_name = 'slip-velocity'
    _python_name = 'slip_velocity'
    return_type = 'object'

class velocity_ratio(Group):
    """
    'velocity_ratio' child.
    """
    _version = '222'
    fluent_name = 'velocity-ratio'
    _python_name = 'velocity_ratio'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class volume_frac(Group):
    """
    'volume_frac' child.
    """
    _version = '222'
    fluent_name = 'volume-frac'
    _python_name = 'volume_frac'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class phase_9_child(Group):
    """
    'child_object_type' of phase.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'phase_child'
    child_names = ['geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'open_channel', 'inlet_number', 'phase_spec', 'ht_local', 'ht_bottom', 'den_spec', 'frame_of_reference', 'flow_spec', 'mass_flow', 'ec_mass_flow', 'mass_flux', 'mass_flux_ave', 'tref', 'pref', 'upstream_torque', 'upstream_t_enthalpy', 't0', 'supersonic_or_initial_gauge_pressure', 'direction_spec', 'coordinate_system', 'flow_direction_component', 'direction_vector_components', 'axis_direction_component', 'axis_origin_component', 'ke_spec', 'nut', 'kl', 'intermit', 'k', 'e', 'o', 'v2', 'turb_intensity', 'turb_length_scale', 'turb_hydraulic_diam', 'turb_viscosity_ratio', 'turb_viscosity_ratio_profile', 'rst_spec', 'uu', 'vv', 'ww', 'uv', 'vw', 'uw', 'ksgs_spec', 'ksgs', 'sgs_turb_intensity', 'species_in_mole_fractions', 'mf', 'elec_potential_type', 'potential_value', 'dual_potential_type', 'dual_potential_value', 'x_displacement_type', 'x_displacement_value', 'y_displacement_type', 'y_displacement_value', 'z_displacement_type', 'z_displacement_value', 'prob_mode_1', 'prob_mode_2', 'prob_mode_3', 'equ_required', 'swirl_model', 'swirl_factor', 'x_fan_origin', 'y_fan_origin', 'z_fan_origin', 'fan_origin_components', 'premixc', 'premixc_var', 'ecfm_sigma', 'inert', 'pollut_no', 'pollut_hcn', 'pollut_nh3', 'pollut_n2o', 'pollut_urea', 'pollut_hnco', 'pollut_nco', 'pollut_so2', 'pollut_h2s', 'pollut_so3', 'pollut_sh', 'pollut_so', 'pollut_soot', 'pollut_nuclei', 'pollut_ctar', 'pollut_hg', 'pollut_hgcl2', 'pollut_hcl', 'pollut_hgo', 'pollut_cl', 'pollut_cl2', 'pollut_hgcl', 'pollut_hocl', 'fensapice_flow_bc_subtype', 'fensapice_drop_bccustom', 'fensapice_drop_lwc', 'fensapice_drop_dtemp', 'fensapice_drop_ddiam', 'fensapice_drop_dv', 'fensapice_drop_dx', 'fensapice_drop_dy', 'fensapice_drop_dz', 'fensapice_dpm_surface_injection', 'fensapice_dpm_inj_nstream', 'fensapice_drop_icc', 'fensapice_drop_ctemp', 'fensapice_drop_cdiam', 'fensapice_drop_cv', 'fensapice_drop_cx', 'fensapice_drop_cy', 'fensapice_drop_cz', 'fensapice_drop_vrh', 'fensapice_drop_vrh_1', 'fensapice_drop_vc', 'radiation_bc', 'radial_direction_component', 'coll_dtheta', 'coll_dphi', 'band_q_irrad', 'band_q_irrad_diffuse', 'parallel_collimated_beam', 'solar_direction', 'solar_irradiation', 't_b_b_spec', 't_b_b', 'in_emiss', 'fmean', 'fvar', 'fmean2', 'fvar2', 'tss_scalar', 'uds_bc', 'uds', 'pb_disc_bc', 'pb_disc', 'pb_qmom_bc', 'pb_qmom', 'pb_smm_bc', 'pb_smm', 'pb_dqmom_bc', 'pb_dqmom', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'mixing_plane_thread', 'wsf', 'wsb', 'wsn', 'solar_fluxes', 'solar_shining_factor', 'radiating_s2s_surface', 'slip_velocity', 'velocity_ratio', 'volume_frac', 'granular_temperature', 'iac', 'ac_options', 'impedance_0', 'impedance_1', 'impedance_2', 'ac_wave']
    _child_classes = dict(
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        open_channel=open_channel,
        inlet_number=inlet_number,
        phase_spec=phase_spec,
        ht_local=ht_local,
        ht_bottom=ht_bottom,
        den_spec=den_spec,
        frame_of_reference=frame_of_reference,
        flow_spec=flow_spec,
        mass_flow=mass_flow,
        ec_mass_flow=ec_mass_flow,
        mass_flux=mass_flux,
        mass_flux_ave=mass_flux_ave,
        tref=tref,
        pref=pref,
        upstream_torque=upstream_torque,
        upstream_t_enthalpy=upstream_t_enthalpy,
        t0=t0,
        supersonic_or_initial_gauge_pressure=supersonic_or_initial_gauge_pressure,
        direction_spec=direction_spec,
        coordinate_system=coordinate_system,
        flow_direction_component=flow_direction_component,
        direction_vector_components=direction_vector_components,
        axis_direction_component=axis_direction_component_1,
        axis_origin_component=axis_origin_component_1,
        ke_spec=ke_spec,
        nut=nut,
        kl=kl,
        intermit=intermit,
        k=k,
        e=e,
        o=o,
        v2=v2,
        turb_intensity=turb_intensity,
        turb_length_scale=turb_length_scale,
        turb_hydraulic_diam=turb_hydraulic_diam,
        turb_viscosity_ratio=turb_viscosity_ratio,
        turb_viscosity_ratio_profile=turb_viscosity_ratio_profile,
        rst_spec=rst_spec,
        uu=uu,
        vv=vv,
        ww=ww,
        uv=uv,
        vw=vw,
        uw=uw,
        ksgs_spec=ksgs_spec,
        ksgs=ksgs,
        sgs_turb_intensity=sgs_turb_intensity,
        species_in_mole_fractions=species_in_mole_fractions,
        mf=mf,
        elec_potential_type=elec_potential_type,
        potential_value=potential_value,
        dual_potential_type=dual_potential_type,
        dual_potential_value=dual_potential_value,
        x_displacement_type=x_displacement_type,
        x_displacement_value=x_displacement_value,
        y_displacement_type=y_displacement_type,
        y_displacement_value=y_displacement_value,
        z_displacement_type=z_displacement_type,
        z_displacement_value=z_displacement_value,
        prob_mode_1=prob_mode_1,
        prob_mode_2=prob_mode_2,
        prob_mode_3=prob_mode_3,
        equ_required=equ_required,
        swirl_model=swirl_model,
        swirl_factor=swirl_factor,
        x_fan_origin=x_fan_origin,
        y_fan_origin=y_fan_origin,
        z_fan_origin=z_fan_origin,
        fan_origin_components=fan_origin_components,
        premixc=premixc,
        premixc_var=premixc_var,
        ecfm_sigma=ecfm_sigma,
        inert=inert,
        pollut_no=pollut_no,
        pollut_hcn=pollut_hcn,
        pollut_nh3=pollut_nh3,
        pollut_n2o=pollut_n2o,
        pollut_urea=pollut_urea,
        pollut_hnco=pollut_hnco,
        pollut_nco=pollut_nco,
        pollut_so2=pollut_so2,
        pollut_h2s=pollut_h2s,
        pollut_so3=pollut_so3,
        pollut_sh=pollut_sh,
        pollut_so=pollut_so,
        pollut_soot=pollut_soot,
        pollut_nuclei=pollut_nuclei,
        pollut_ctar=pollut_ctar,
        pollut_hg=pollut_hg,
        pollut_hgcl2=pollut_hgcl2,
        pollut_hcl=pollut_hcl,
        pollut_hgo=pollut_hgo,
        pollut_cl=pollut_cl,
        pollut_cl2=pollut_cl2,
        pollut_hgcl=pollut_hgcl,
        pollut_hocl=pollut_hocl,
        fensapice_flow_bc_subtype=fensapice_flow_bc_subtype,
        fensapice_drop_bccustom=fensapice_drop_bccustom,
        fensapice_drop_lwc=fensapice_drop_lwc,
        fensapice_drop_dtemp=fensapice_drop_dtemp,
        fensapice_drop_ddiam=fensapice_drop_ddiam,
        fensapice_drop_dv=fensapice_drop_dv,
        fensapice_drop_dx=fensapice_drop_dx,
        fensapice_drop_dy=fensapice_drop_dy,
        fensapice_drop_dz=fensapice_drop_dz,
        fensapice_dpm_surface_injection=fensapice_dpm_surface_injection,
        fensapice_dpm_inj_nstream=fensapice_dpm_inj_nstream,
        fensapice_drop_icc=fensapice_drop_icc,
        fensapice_drop_ctemp=fensapice_drop_ctemp,
        fensapice_drop_cdiam=fensapice_drop_cdiam,
        fensapice_drop_cv=fensapice_drop_cv,
        fensapice_drop_cx=fensapice_drop_cx,
        fensapice_drop_cy=fensapice_drop_cy,
        fensapice_drop_cz=fensapice_drop_cz,
        fensapice_drop_vrh=fensapice_drop_vrh,
        fensapice_drop_vrh_1=fensapice_drop_vrh_1,
        fensapice_drop_vc=fensapice_drop_vc,
        radiation_bc=radiation_bc,
        radial_direction_component=radial_direction_component,
        coll_dtheta=coll_dtheta,
        coll_dphi=coll_dphi,
        band_q_irrad=band_q_irrad,
        band_q_irrad_diffuse=band_q_irrad_diffuse,
        parallel_collimated_beam=parallel_collimated_beam,
        solar_direction=solar_direction,
        solar_irradiation=solar_irradiation,
        t_b_b_spec=t_b_b_spec,
        t_b_b=t_b_b,
        in_emiss=in_emiss,
        fmean=fmean,
        fvar=fvar,
        fmean2=fmean2,
        fvar2=fvar2,
        tss_scalar=tss_scalar,
        uds_bc=uds_bc,
        uds=uds,
        pb_disc_bc=pb_disc_bc,
        pb_disc=pb_disc,
        pb_qmom_bc=pb_qmom_bc,
        pb_qmom=pb_qmom,
        pb_smm_bc=pb_smm_bc,
        pb_smm=pb_smm,
        pb_dqmom_bc=pb_dqmom_bc,
        pb_dqmom=pb_dqmom,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        mixing_plane_thread=mixing_plane_thread,
        wsf=wsf,
        wsb=wsb,
        wsn=wsn,
        solar_fluxes=solar_fluxes,
        solar_shining_factor=solar_shining_factor,
        radiating_s2s_surface=radiating_s2s_surface,
        slip_velocity=slip_velocity,
        velocity_ratio=velocity_ratio,
        volume_frac=volume_frac,
        granular_temperature=granular_temperature,
        iac=iac,
        ac_options=ac_options,
        impedance_0=impedance_0,
        impedance_1=impedance_1,
        impedance_2=impedance_2,
        ac_wave=ac_wave,
    )
    return_type = 'object'

class phase_9(NamedObject[phase_9_child], CreatableNamedObjectMixinOld[phase_9_child]):
    """
    'phase' child.
    """
    _version = '222'
    fluent_name = 'phase'
    _python_name = 'phase'
    child_object_type = phase_9_child
    return_type = 'object'

class mass_flow_inlet_child(Group):
    """
    'child_object_type' of mass_flow_inlet.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'mass_flow_inlet_child'
    child_names = ['phase', 'geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'open_channel', 'inlet_number', 'phase_spec', 'ht_local', 'ht_bottom', 'den_spec', 'frame_of_reference', 'flow_spec', 'mass_flow', 'ec_mass_flow', 'mass_flux', 'mass_flux_ave', 'tref', 'pref', 'upstream_torque', 'upstream_t_enthalpy', 't0', 'supersonic_or_initial_gauge_pressure', 'direction_spec', 'coordinate_system', 'flow_direction_component', 'direction_vector_components', 'axis_direction_component', 'axis_origin_component', 'ke_spec', 'nut', 'kl', 'intermit', 'k', 'e', 'o', 'v2', 'turb_intensity', 'turb_length_scale', 'turb_hydraulic_diam', 'turb_viscosity_ratio', 'turb_viscosity_ratio_profile', 'rst_spec', 'uu', 'vv', 'ww', 'uv', 'vw', 'uw', 'ksgs_spec', 'ksgs', 'sgs_turb_intensity', 'species_in_mole_fractions', 'mf', 'elec_potential_type', 'potential_value', 'dual_potential_type', 'dual_potential_value', 'x_displacement_type', 'x_displacement_value', 'y_displacement_type', 'y_displacement_value', 'z_displacement_type', 'z_displacement_value', 'prob_mode_1', 'prob_mode_2', 'prob_mode_3', 'equ_required', 'swirl_model', 'swirl_factor', 'x_fan_origin', 'y_fan_origin', 'z_fan_origin', 'fan_origin_components', 'premixc', 'premixc_var', 'ecfm_sigma', 'inert', 'pollut_no', 'pollut_hcn', 'pollut_nh3', 'pollut_n2o', 'pollut_urea', 'pollut_hnco', 'pollut_nco', 'pollut_so2', 'pollut_h2s', 'pollut_so3', 'pollut_sh', 'pollut_so', 'pollut_soot', 'pollut_nuclei', 'pollut_ctar', 'pollut_hg', 'pollut_hgcl2', 'pollut_hcl', 'pollut_hgo', 'pollut_cl', 'pollut_cl2', 'pollut_hgcl', 'pollut_hocl', 'fensapice_flow_bc_subtype', 'fensapice_drop_bccustom', 'fensapice_drop_lwc', 'fensapice_drop_dtemp', 'fensapice_drop_ddiam', 'fensapice_drop_dv', 'fensapice_drop_dx', 'fensapice_drop_dy', 'fensapice_drop_dz', 'fensapice_dpm_surface_injection', 'fensapice_dpm_inj_nstream', 'fensapice_drop_icc', 'fensapice_drop_ctemp', 'fensapice_drop_cdiam', 'fensapice_drop_cv', 'fensapice_drop_cx', 'fensapice_drop_cy', 'fensapice_drop_cz', 'fensapice_drop_vrh', 'fensapice_drop_vrh_1', 'fensapice_drop_vc', 'radiation_bc', 'radial_direction_component', 'coll_dtheta', 'coll_dphi', 'band_q_irrad', 'band_q_irrad_diffuse', 'parallel_collimated_beam', 'solar_direction', 'solar_irradiation', 't_b_b_spec', 't_b_b', 'in_emiss', 'fmean', 'fvar', 'fmean2', 'fvar2', 'tss_scalar', 'uds_bc', 'uds', 'pb_disc_bc', 'pb_disc', 'pb_qmom_bc', 'pb_qmom', 'pb_smm_bc', 'pb_smm', 'pb_dqmom_bc', 'pb_dqmom', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'mixing_plane_thread', 'wsf', 'wsb', 'wsn', 'solar_fluxes', 'solar_shining_factor', 'radiating_s2s_surface', 'slip_velocity', 'velocity_ratio', 'volume_frac', 'granular_temperature', 'iac', 'ac_options', 'impedance_0', 'impedance_1', 'impedance_2', 'ac_wave']
    _child_classes = dict(
        phase=phase_9,
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        open_channel=open_channel,
        inlet_number=inlet_number,
        phase_spec=phase_spec,
        ht_local=ht_local,
        ht_bottom=ht_bottom,
        den_spec=den_spec,
        frame_of_reference=frame_of_reference,
        flow_spec=flow_spec,
        mass_flow=mass_flow,
        ec_mass_flow=ec_mass_flow,
        mass_flux=mass_flux,
        mass_flux_ave=mass_flux_ave,
        tref=tref,
        pref=pref,
        upstream_torque=upstream_torque,
        upstream_t_enthalpy=upstream_t_enthalpy,
        t0=t0,
        supersonic_or_initial_gauge_pressure=supersonic_or_initial_gauge_pressure,
        direction_spec=direction_spec,
        coordinate_system=coordinate_system,
        flow_direction_component=flow_direction_component,
        direction_vector_components=direction_vector_components,
        axis_direction_component=axis_direction_component_1,
        axis_origin_component=axis_origin_component_1,
        ke_spec=ke_spec,
        nut=nut,
        kl=kl,
        intermit=intermit,
        k=k,
        e=e,
        o=o,
        v2=v2,
        turb_intensity=turb_intensity,
        turb_length_scale=turb_length_scale,
        turb_hydraulic_diam=turb_hydraulic_diam,
        turb_viscosity_ratio=turb_viscosity_ratio,
        turb_viscosity_ratio_profile=turb_viscosity_ratio_profile,
        rst_spec=rst_spec,
        uu=uu,
        vv=vv,
        ww=ww,
        uv=uv,
        vw=vw,
        uw=uw,
        ksgs_spec=ksgs_spec,
        ksgs=ksgs,
        sgs_turb_intensity=sgs_turb_intensity,
        species_in_mole_fractions=species_in_mole_fractions,
        mf=mf,
        elec_potential_type=elec_potential_type,
        potential_value=potential_value,
        dual_potential_type=dual_potential_type,
        dual_potential_value=dual_potential_value,
        x_displacement_type=x_displacement_type,
        x_displacement_value=x_displacement_value,
        y_displacement_type=y_displacement_type,
        y_displacement_value=y_displacement_value,
        z_displacement_type=z_displacement_type,
        z_displacement_value=z_displacement_value,
        prob_mode_1=prob_mode_1,
        prob_mode_2=prob_mode_2,
        prob_mode_3=prob_mode_3,
        equ_required=equ_required,
        swirl_model=swirl_model,
        swirl_factor=swirl_factor,
        x_fan_origin=x_fan_origin,
        y_fan_origin=y_fan_origin,
        z_fan_origin=z_fan_origin,
        fan_origin_components=fan_origin_components,
        premixc=premixc,
        premixc_var=premixc_var,
        ecfm_sigma=ecfm_sigma,
        inert=inert,
        pollut_no=pollut_no,
        pollut_hcn=pollut_hcn,
        pollut_nh3=pollut_nh3,
        pollut_n2o=pollut_n2o,
        pollut_urea=pollut_urea,
        pollut_hnco=pollut_hnco,
        pollut_nco=pollut_nco,
        pollut_so2=pollut_so2,
        pollut_h2s=pollut_h2s,
        pollut_so3=pollut_so3,
        pollut_sh=pollut_sh,
        pollut_so=pollut_so,
        pollut_soot=pollut_soot,
        pollut_nuclei=pollut_nuclei,
        pollut_ctar=pollut_ctar,
        pollut_hg=pollut_hg,
        pollut_hgcl2=pollut_hgcl2,
        pollut_hcl=pollut_hcl,
        pollut_hgo=pollut_hgo,
        pollut_cl=pollut_cl,
        pollut_cl2=pollut_cl2,
        pollut_hgcl=pollut_hgcl,
        pollut_hocl=pollut_hocl,
        fensapice_flow_bc_subtype=fensapice_flow_bc_subtype,
        fensapice_drop_bccustom=fensapice_drop_bccustom,
        fensapice_drop_lwc=fensapice_drop_lwc,
        fensapice_drop_dtemp=fensapice_drop_dtemp,
        fensapice_drop_ddiam=fensapice_drop_ddiam,
        fensapice_drop_dv=fensapice_drop_dv,
        fensapice_drop_dx=fensapice_drop_dx,
        fensapice_drop_dy=fensapice_drop_dy,
        fensapice_drop_dz=fensapice_drop_dz,
        fensapice_dpm_surface_injection=fensapice_dpm_surface_injection,
        fensapice_dpm_inj_nstream=fensapice_dpm_inj_nstream,
        fensapice_drop_icc=fensapice_drop_icc,
        fensapice_drop_ctemp=fensapice_drop_ctemp,
        fensapice_drop_cdiam=fensapice_drop_cdiam,
        fensapice_drop_cv=fensapice_drop_cv,
        fensapice_drop_cx=fensapice_drop_cx,
        fensapice_drop_cy=fensapice_drop_cy,
        fensapice_drop_cz=fensapice_drop_cz,
        fensapice_drop_vrh=fensapice_drop_vrh,
        fensapice_drop_vrh_1=fensapice_drop_vrh_1,
        fensapice_drop_vc=fensapice_drop_vc,
        radiation_bc=radiation_bc,
        radial_direction_component=radial_direction_component,
        coll_dtheta=coll_dtheta,
        coll_dphi=coll_dphi,
        band_q_irrad=band_q_irrad,
        band_q_irrad_diffuse=band_q_irrad_diffuse,
        parallel_collimated_beam=parallel_collimated_beam,
        solar_direction=solar_direction,
        solar_irradiation=solar_irradiation,
        t_b_b_spec=t_b_b_spec,
        t_b_b=t_b_b,
        in_emiss=in_emiss,
        fmean=fmean,
        fvar=fvar,
        fmean2=fmean2,
        fvar2=fvar2,
        tss_scalar=tss_scalar,
        uds_bc=uds_bc,
        uds=uds,
        pb_disc_bc=pb_disc_bc,
        pb_disc=pb_disc,
        pb_qmom_bc=pb_qmom_bc,
        pb_qmom=pb_qmom,
        pb_smm_bc=pb_smm_bc,
        pb_smm=pb_smm,
        pb_dqmom_bc=pb_dqmom_bc,
        pb_dqmom=pb_dqmom,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        mixing_plane_thread=mixing_plane_thread,
        wsf=wsf,
        wsb=wsb,
        wsn=wsn,
        solar_fluxes=solar_fluxes,
        solar_shining_factor=solar_shining_factor,
        radiating_s2s_surface=radiating_s2s_surface,
        slip_velocity=slip_velocity,
        velocity_ratio=velocity_ratio,
        volume_frac=volume_frac,
        granular_temperature=granular_temperature,
        iac=iac,
        ac_options=ac_options,
        impedance_0=impedance_0,
        impedance_1=impedance_1,
        impedance_2=impedance_2,
        ac_wave=ac_wave,
    )
    return_type = 'object'

class mass_flow_inlet(NamedObject[mass_flow_inlet_child], CreatableNamedObjectMixinOld[mass_flow_inlet_child]):
    """
    'mass_flow_inlet' child.
    """
    _version = '222'
    fluent_name = 'mass-flow-inlet'
    _python_name = 'mass_flow_inlet'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = mass_flow_inlet_child
    return_type = 'object'

class mass_flow_outlet_child(Group):
    """
    'child_object_type' of mass_flow_outlet.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'mass_flow_outlet_child'
    child_names = ['phase', 'geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'open_channel', 'inlet_number', 'phase_spec', 'ht_local', 'ht_bottom', 'den_spec', 'frame_of_reference', 'flow_spec', 'mass_flow', 'ec_mass_flow', 'mass_flux', 'mass_flux_ave', 'tref', 'pref', 'upstream_torque', 'upstream_t_enthalpy', 't0', 'supersonic_or_initial_gauge_pressure', 'direction_spec', 'coordinate_system', 'flow_direction_component', 'direction_vector_components', 'axis_direction_component', 'axis_origin_component', 'ke_spec', 'nut', 'kl', 'intermit', 'k', 'e', 'o', 'v2', 'turb_intensity', 'turb_length_scale', 'turb_hydraulic_diam', 'turb_viscosity_ratio', 'turb_viscosity_ratio_profile', 'rst_spec', 'uu', 'vv', 'ww', 'uv', 'vw', 'uw', 'ksgs_spec', 'ksgs', 'sgs_turb_intensity', 'species_in_mole_fractions', 'mf', 'elec_potential_type', 'potential_value', 'dual_potential_type', 'dual_potential_value', 'x_displacement_type', 'x_displacement_value', 'y_displacement_type', 'y_displacement_value', 'z_displacement_type', 'z_displacement_value', 'prob_mode_1', 'prob_mode_2', 'prob_mode_3', 'equ_required', 'swirl_model', 'swirl_factor', 'x_fan_origin', 'y_fan_origin', 'z_fan_origin', 'fan_origin_components', 'premixc', 'premixc_var', 'ecfm_sigma', 'inert', 'pollut_no', 'pollut_hcn', 'pollut_nh3', 'pollut_n2o', 'pollut_urea', 'pollut_hnco', 'pollut_nco', 'pollut_so2', 'pollut_h2s', 'pollut_so3', 'pollut_sh', 'pollut_so', 'pollut_soot', 'pollut_nuclei', 'pollut_ctar', 'pollut_hg', 'pollut_hgcl2', 'pollut_hcl', 'pollut_hgo', 'pollut_cl', 'pollut_cl2', 'pollut_hgcl', 'pollut_hocl', 'fensapice_flow_bc_subtype', 'fensapice_drop_bccustom', 'fensapice_drop_lwc', 'fensapice_drop_dtemp', 'fensapice_drop_ddiam', 'fensapice_drop_dv', 'fensapice_drop_dx', 'fensapice_drop_dy', 'fensapice_drop_dz', 'fensapice_dpm_surface_injection', 'fensapice_dpm_inj_nstream', 'fensapice_drop_icc', 'fensapice_drop_ctemp', 'fensapice_drop_cdiam', 'fensapice_drop_cv', 'fensapice_drop_cx', 'fensapice_drop_cy', 'fensapice_drop_cz', 'fensapice_drop_vrh', 'fensapice_drop_vrh_1', 'fensapice_drop_vc', 'radiation_bc', 'radial_direction_component', 'coll_dtheta', 'coll_dphi', 'band_q_irrad', 'band_q_irrad_diffuse', 'parallel_collimated_beam', 'solar_direction', 'solar_irradiation', 't_b_b_spec', 't_b_b', 'in_emiss', 'fmean', 'fvar', 'fmean2', 'fvar2', 'tss_scalar', 'uds_bc', 'uds', 'pb_disc_bc', 'pb_disc', 'pb_qmom_bc', 'pb_qmom', 'pb_smm_bc', 'pb_smm', 'pb_dqmom_bc', 'pb_dqmom', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'mixing_plane_thread', 'wsf', 'wsb', 'wsn', 'solar_fluxes', 'solar_shining_factor', 'radiating_s2s_surface', 'slip_velocity', 'velocity_ratio', 'volume_frac', 'granular_temperature', 'iac', 'ac_options', 'impedance_0', 'impedance_1', 'impedance_2', 'ac_wave']
    _child_classes = dict(
        phase=phase_9,
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        open_channel=open_channel,
        inlet_number=inlet_number,
        phase_spec=phase_spec,
        ht_local=ht_local,
        ht_bottom=ht_bottom,
        den_spec=den_spec,
        frame_of_reference=frame_of_reference,
        flow_spec=flow_spec,
        mass_flow=mass_flow,
        ec_mass_flow=ec_mass_flow,
        mass_flux=mass_flux,
        mass_flux_ave=mass_flux_ave,
        tref=tref,
        pref=pref,
        upstream_torque=upstream_torque,
        upstream_t_enthalpy=upstream_t_enthalpy,
        t0=t0,
        supersonic_or_initial_gauge_pressure=supersonic_or_initial_gauge_pressure,
        direction_spec=direction_spec,
        coordinate_system=coordinate_system,
        flow_direction_component=flow_direction_component,
        direction_vector_components=direction_vector_components,
        axis_direction_component=axis_direction_component_1,
        axis_origin_component=axis_origin_component_1,
        ke_spec=ke_spec,
        nut=nut,
        kl=kl,
        intermit=intermit,
        k=k,
        e=e,
        o=o,
        v2=v2,
        turb_intensity=turb_intensity,
        turb_length_scale=turb_length_scale,
        turb_hydraulic_diam=turb_hydraulic_diam,
        turb_viscosity_ratio=turb_viscosity_ratio,
        turb_viscosity_ratio_profile=turb_viscosity_ratio_profile,
        rst_spec=rst_spec,
        uu=uu,
        vv=vv,
        ww=ww,
        uv=uv,
        vw=vw,
        uw=uw,
        ksgs_spec=ksgs_spec,
        ksgs=ksgs,
        sgs_turb_intensity=sgs_turb_intensity,
        species_in_mole_fractions=species_in_mole_fractions,
        mf=mf,
        elec_potential_type=elec_potential_type,
        potential_value=potential_value,
        dual_potential_type=dual_potential_type,
        dual_potential_value=dual_potential_value,
        x_displacement_type=x_displacement_type,
        x_displacement_value=x_displacement_value,
        y_displacement_type=y_displacement_type,
        y_displacement_value=y_displacement_value,
        z_displacement_type=z_displacement_type,
        z_displacement_value=z_displacement_value,
        prob_mode_1=prob_mode_1,
        prob_mode_2=prob_mode_2,
        prob_mode_3=prob_mode_3,
        equ_required=equ_required,
        swirl_model=swirl_model,
        swirl_factor=swirl_factor,
        x_fan_origin=x_fan_origin,
        y_fan_origin=y_fan_origin,
        z_fan_origin=z_fan_origin,
        fan_origin_components=fan_origin_components,
        premixc=premixc,
        premixc_var=premixc_var,
        ecfm_sigma=ecfm_sigma,
        inert=inert,
        pollut_no=pollut_no,
        pollut_hcn=pollut_hcn,
        pollut_nh3=pollut_nh3,
        pollut_n2o=pollut_n2o,
        pollut_urea=pollut_urea,
        pollut_hnco=pollut_hnco,
        pollut_nco=pollut_nco,
        pollut_so2=pollut_so2,
        pollut_h2s=pollut_h2s,
        pollut_so3=pollut_so3,
        pollut_sh=pollut_sh,
        pollut_so=pollut_so,
        pollut_soot=pollut_soot,
        pollut_nuclei=pollut_nuclei,
        pollut_ctar=pollut_ctar,
        pollut_hg=pollut_hg,
        pollut_hgcl2=pollut_hgcl2,
        pollut_hcl=pollut_hcl,
        pollut_hgo=pollut_hgo,
        pollut_cl=pollut_cl,
        pollut_cl2=pollut_cl2,
        pollut_hgcl=pollut_hgcl,
        pollut_hocl=pollut_hocl,
        fensapice_flow_bc_subtype=fensapice_flow_bc_subtype,
        fensapice_drop_bccustom=fensapice_drop_bccustom,
        fensapice_drop_lwc=fensapice_drop_lwc,
        fensapice_drop_dtemp=fensapice_drop_dtemp,
        fensapice_drop_ddiam=fensapice_drop_ddiam,
        fensapice_drop_dv=fensapice_drop_dv,
        fensapice_drop_dx=fensapice_drop_dx,
        fensapice_drop_dy=fensapice_drop_dy,
        fensapice_drop_dz=fensapice_drop_dz,
        fensapice_dpm_surface_injection=fensapice_dpm_surface_injection,
        fensapice_dpm_inj_nstream=fensapice_dpm_inj_nstream,
        fensapice_drop_icc=fensapice_drop_icc,
        fensapice_drop_ctemp=fensapice_drop_ctemp,
        fensapice_drop_cdiam=fensapice_drop_cdiam,
        fensapice_drop_cv=fensapice_drop_cv,
        fensapice_drop_cx=fensapice_drop_cx,
        fensapice_drop_cy=fensapice_drop_cy,
        fensapice_drop_cz=fensapice_drop_cz,
        fensapice_drop_vrh=fensapice_drop_vrh,
        fensapice_drop_vrh_1=fensapice_drop_vrh_1,
        fensapice_drop_vc=fensapice_drop_vc,
        radiation_bc=radiation_bc,
        radial_direction_component=radial_direction_component,
        coll_dtheta=coll_dtheta,
        coll_dphi=coll_dphi,
        band_q_irrad=band_q_irrad,
        band_q_irrad_diffuse=band_q_irrad_diffuse,
        parallel_collimated_beam=parallel_collimated_beam,
        solar_direction=solar_direction,
        solar_irradiation=solar_irradiation,
        t_b_b_spec=t_b_b_spec,
        t_b_b=t_b_b,
        in_emiss=in_emiss,
        fmean=fmean,
        fvar=fvar,
        fmean2=fmean2,
        fvar2=fvar2,
        tss_scalar=tss_scalar,
        uds_bc=uds_bc,
        uds=uds,
        pb_disc_bc=pb_disc_bc,
        pb_disc=pb_disc,
        pb_qmom_bc=pb_qmom_bc,
        pb_qmom=pb_qmom,
        pb_smm_bc=pb_smm_bc,
        pb_smm=pb_smm,
        pb_dqmom_bc=pb_dqmom_bc,
        pb_dqmom=pb_dqmom,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        mixing_plane_thread=mixing_plane_thread,
        wsf=wsf,
        wsb=wsb,
        wsn=wsn,
        solar_fluxes=solar_fluxes,
        solar_shining_factor=solar_shining_factor,
        radiating_s2s_surface=radiating_s2s_surface,
        slip_velocity=slip_velocity,
        velocity_ratio=velocity_ratio,
        volume_frac=volume_frac,
        granular_temperature=granular_temperature,
        iac=iac,
        ac_options=ac_options,
        impedance_0=impedance_0,
        impedance_1=impedance_1,
        impedance_2=impedance_2,
        ac_wave=ac_wave,
    )
    return_type = 'object'

class mass_flow_outlet(NamedObject[mass_flow_outlet_child], CreatableNamedObjectMixinOld[mass_flow_outlet_child]):
    """
    'mass_flow_outlet' child.
    """
    _version = '222'
    fluent_name = 'mass-flow-outlet'
    _python_name = 'mass_flow_outlet'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = mass_flow_outlet_child
    return_type = 'object'

class phase_10_child(Group):
    """
    'child_object_type' of phase.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'phase_child'
    return_type = 'object'

class phase_10(NamedObject[phase_10_child], CreatableNamedObjectMixinOld[phase_10_child]):
    """
    'phase' child.
    """
    _version = '222'
    fluent_name = 'phase'
    _python_name = 'phase'
    child_object_type = phase_10_child
    return_type = 'object'

class network_child(Group):
    """
    'child_object_type' of network.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'network_child'
    child_names = ['phase']
    _child_classes = dict(
        phase=phase_10,
    )
    return_type = 'object'

class network(NamedObject[network_child], CreatableNamedObjectMixinOld[network_child]):
    """
    'network' child.
    """
    _version = '222'
    fluent_name = 'network'
    _python_name = 'network'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = network_child
    return_type = 'object'

class thermal_bc(String, AllowedValuesMixin):
    """
    'thermal_bc' child.
    """
    _version = '222'
    fluent_name = 'thermal-bc'
    _python_name = 'thermal_bc'
    return_type = 'object'

class temperature(Group):
    """
    'temperature' child.
    """
    _version = '222'
    fluent_name = 'temperature'
    _python_name = 'temperature'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class q(Group):
    """
    'q' child.
    """
    _version = '222'
    fluent_name = 'q'
    _python_name = 'q'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class phase_11_child(Group):
    """
    'child_object_type' of phase.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'phase_child'
    child_names = ['thermal_bc', 'temperature', 'q']
    _child_classes = dict(
        thermal_bc=thermal_bc,
        temperature=temperature,
        q=q,
    )
    return_type = 'object'

class phase_11(NamedObject[phase_11_child], CreatableNamedObjectMixinOld[phase_11_child]):
    """
    'phase' child.
    """
    _version = '222'
    fluent_name = 'phase'
    _python_name = 'phase'
    child_object_type = phase_11_child
    return_type = 'object'

class network_end_child(Group):
    """
    'child_object_type' of network_end.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'network_end_child'
    child_names = ['phase', 'thermal_bc', 'temperature', 'q']
    _child_classes = dict(
        phase=phase_11,
        thermal_bc=thermal_bc,
        temperature=temperature,
        q=q,
    )
    return_type = 'object'

class network_end(NamedObject[network_end_child], CreatableNamedObjectMixinOld[network_end_child]):
    """
    'network_end' child.
    """
    _version = '222'
    fluent_name = 'network-end'
    _python_name = 'network_end'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = network_end_child
    return_type = 'object'

class flowrate_frac(Real, AllowedValuesMixin):
    """
    'flowrate_frac' child.
    """
    _version = '222'
    fluent_name = 'flowrate-frac'
    _python_name = 'flowrate_frac'
    return_type = 'object'

class phase_12_child(Group):
    """
    'child_object_type' of phase.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'phase_child'
    child_names = ['geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'flowrate_frac', 'elec_potential_type', 'potential_value', 'dual_potential_type', 'dual_potential_value', 'x_displacement_type', 'x_displacement_value', 'y_displacement_type', 'y_displacement_value', 'z_displacement_type', 'z_displacement_value', 'uds_bc', 'uds', 'radiation_bc', 'coll_dtheta', 'coll_dphi', 'band_q_irrad', 'band_q_irrad_diffuse', 'parallel_collimated_beam', 'solar_direction', 'solar_irradiation', 't_b_b_spec', 't_b_b', 'in_emiss', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'solar_fluxes', 'solar_shining_factor', 'radiating_s2s_surface']
    _child_classes = dict(
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        flowrate_frac=flowrate_frac,
        elec_potential_type=elec_potential_type,
        potential_value=potential_value,
        dual_potential_type=dual_potential_type,
        dual_potential_value=dual_potential_value,
        x_displacement_type=x_displacement_type,
        x_displacement_value=x_displacement_value,
        y_displacement_type=y_displacement_type,
        y_displacement_value=y_displacement_value,
        z_displacement_type=z_displacement_type,
        z_displacement_value=z_displacement_value,
        uds_bc=uds_bc,
        uds=uds,
        radiation_bc=radiation_bc,
        coll_dtheta=coll_dtheta,
        coll_dphi=coll_dphi,
        band_q_irrad=band_q_irrad,
        band_q_irrad_diffuse=band_q_irrad_diffuse,
        parallel_collimated_beam=parallel_collimated_beam,
        solar_direction=solar_direction,
        solar_irradiation=solar_irradiation,
        t_b_b_spec=t_b_b_spec,
        t_b_b=t_b_b,
        in_emiss=in_emiss,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        solar_fluxes=solar_fluxes,
        solar_shining_factor=solar_shining_factor,
        radiating_s2s_surface=radiating_s2s_surface,
    )
    return_type = 'object'

class phase_12(NamedObject[phase_12_child], CreatableNamedObjectMixinOld[phase_12_child]):
    """
    'phase' child.
    """
    _version = '222'
    fluent_name = 'phase'
    _python_name = 'phase'
    child_object_type = phase_12_child
    return_type = 'object'

class outflow_child(Group):
    """
    'child_object_type' of outflow.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'outflow_child'
    child_names = ['phase', 'geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'flowrate_frac', 'elec_potential_type', 'potential_value', 'dual_potential_type', 'dual_potential_value', 'x_displacement_type', 'x_displacement_value', 'y_displacement_type', 'y_displacement_value', 'z_displacement_type', 'z_displacement_value', 'uds_bc', 'uds', 'radiation_bc', 'coll_dtheta', 'coll_dphi', 'band_q_irrad', 'band_q_irrad_diffuse', 'parallel_collimated_beam', 'solar_direction', 'solar_irradiation', 't_b_b_spec', 't_b_b', 'in_emiss', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'solar_fluxes', 'solar_shining_factor', 'radiating_s2s_surface']
    _child_classes = dict(
        phase=phase_12,
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        flowrate_frac=flowrate_frac,
        elec_potential_type=elec_potential_type,
        potential_value=potential_value,
        dual_potential_type=dual_potential_type,
        dual_potential_value=dual_potential_value,
        x_displacement_type=x_displacement_type,
        x_displacement_value=x_displacement_value,
        y_displacement_type=y_displacement_type,
        y_displacement_value=y_displacement_value,
        z_displacement_type=z_displacement_type,
        z_displacement_value=z_displacement_value,
        uds_bc=uds_bc,
        uds=uds,
        radiation_bc=radiation_bc,
        coll_dtheta=coll_dtheta,
        coll_dphi=coll_dphi,
        band_q_irrad=band_q_irrad,
        band_q_irrad_diffuse=band_q_irrad_diffuse,
        parallel_collimated_beam=parallel_collimated_beam,
        solar_direction=solar_direction,
        solar_irradiation=solar_irradiation,
        t_b_b_spec=t_b_b_spec,
        t_b_b=t_b_b,
        in_emiss=in_emiss,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        solar_fluxes=solar_fluxes,
        solar_shining_factor=solar_shining_factor,
        radiating_s2s_surface=radiating_s2s_surface,
    )
    return_type = 'object'

class outflow(NamedObject[outflow_child], CreatableNamedObjectMixinOld[outflow_child]):
    """
    'outflow' child.
    """
    _version = '222'
    fluent_name = 'outflow'
    _python_name = 'outflow'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = outflow_child
    return_type = 'object'

class phase_13_child(Group):
    """
    'child_object_type' of phase.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'phase_child'
    child_names = ['geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'open_channel', 'outlet_number', 'pressure_spec_method', 'press_spec', 'frame_of_reference', 'phase_spec', 'ht_local', 'p', 'p_profile_multiplier', 'ht_bottom', 'den_spec', 't0', 'direction_spec', 'coordinate_system', 'flow_direction_component', 'axis_direction_component', 'axis_origin_component', 'ke_spec', 'nut', 'kl', 'intermit', 'k', 'e', 'o', 'v2', 'turb_intensity', 'turb_length_scale', 'turb_hydraulic_diam', 'turb_viscosity_ratio', 'turb_viscosity_ratio_profile', 'rst_spec', 'uu', 'vv', 'ww', 'uv', 'vw', 'uw', 'ksgs_spec', 'ksgs', 'sgs_turb_intensity', 'radiation_bc', 'radial_direction_component', 'coll_dtheta', 'coll_dphi', 'band_q_irrad', 'band_q_irrad_diffuse', 'parallel_collimated_beam', 'solar_direction', 'solar_irradiation', 't_b_b_spec', 't_b_b', 'in_emiss', 'fmean', 'fmean2', 'fvar', 'fvar2', 'granular_temperature', 'iac', 'lsfun', 'vof_spec', 'volume_fraction', 'species_in_mole_fractions', 'mf', 'elec_potential_type', 'potential_value', 'dual_potential_type', 'dual_potential_value', 'x_displacement_type', 'x_displacement_value', 'y_displacement_type', 'y_displacement_value', 'z_displacement_type', 'z_displacement_value', 'prob_mode_1', 'prob_mode_2', 'prob_mode_3', 'premixc', 'premixc_var', 'ecfm_sigma', 'inert', 'pollut_no', 'pollut_hcn', 'pollut_nh3', 'pollut_n2o', 'pollut_urea', 'pollut_hnco', 'pollut_nco', 'pollut_so2', 'pollut_h2s', 'pollut_so3', 'pollut_sh', 'pollut_so', 'pollut_soot', 'pollut_nuclei', 'pollut_ctar', 'pollut_hg', 'pollut_hgcl2', 'pollut_hcl', 'pollut_hgo', 'pollut_cl', 'pollut_cl2', 'pollut_hgcl', 'pollut_hocl', 'tss_scalar', 'fensapice_flow_bc_subtype', 'uds_bc', 'uds', 'pb_disc_bc', 'pb_disc', 'pb_qmom_bc', 'pb_qmom', 'pb_smm_bc', 'pb_smm', 'pb_dqmom_bc', 'pb_dqmom', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'mixing_plane_thread', 'ac_options', 'p_backflow_spec', 'p_backflow_spec_gen', 'impedance_0', 'impedance_1', 'impedance_2', 'ac_wave', 'prevent_reverse_flow', 'radial', 'avg_press_spec', 'press_averaging_method', 'targeted_mf_boundary', 'targeted_mf', 'targeted_mf_pmax', 'targeted_mf_pmin', 'gen_nrbc_spec', 'wsf', 'wsb', 'wsn', 'solar_fluxes', 'solar_shining_factor', 'radiating_s2s_surface', 'b', 'strength']
    _child_classes = dict(
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        open_channel=open_channel,
        outlet_number=outlet_number,
        pressure_spec_method=pressure_spec_method,
        press_spec=press_spec,
        frame_of_reference=frame_of_reference,
        phase_spec=phase_spec,
        ht_local=ht_local,
        p=p,
        p_profile_multiplier=p_profile_multiplier,
        ht_bottom=ht_bottom,
        den_spec=den_spec,
        t0=t0,
        direction_spec=direction_spec,
        coordinate_system=coordinate_system,
        flow_direction_component=flow_direction_component,
        axis_direction_component=axis_direction_component_1,
        axis_origin_component=axis_origin_component_1,
        ke_spec=ke_spec,
        nut=nut,
        kl=kl,
        intermit=intermit,
        k=k,
        e=e,
        o=o,
        v2=v2,
        turb_intensity=turb_intensity,
        turb_length_scale=turb_length_scale,
        turb_hydraulic_diam=turb_hydraulic_diam,
        turb_viscosity_ratio=turb_viscosity_ratio,
        turb_viscosity_ratio_profile=turb_viscosity_ratio_profile,
        rst_spec=rst_spec,
        uu=uu,
        vv=vv,
        ww=ww,
        uv=uv,
        vw=vw,
        uw=uw,
        ksgs_spec=ksgs_spec,
        ksgs=ksgs,
        sgs_turb_intensity=sgs_turb_intensity,
        radiation_bc=radiation_bc,
        radial_direction_component=radial_direction_component,
        coll_dtheta=coll_dtheta,
        coll_dphi=coll_dphi,
        band_q_irrad=band_q_irrad,
        band_q_irrad_diffuse=band_q_irrad_diffuse,
        parallel_collimated_beam=parallel_collimated_beam,
        solar_direction=solar_direction,
        solar_irradiation=solar_irradiation,
        t_b_b_spec=t_b_b_spec,
        t_b_b=t_b_b,
        in_emiss=in_emiss,
        fmean=fmean,
        fmean2=fmean2,
        fvar=fvar,
        fvar2=fvar2,
        granular_temperature=granular_temperature,
        iac=iac,
        lsfun=lsfun,
        vof_spec=vof_spec,
        volume_fraction=volume_fraction,
        species_in_mole_fractions=species_in_mole_fractions,
        mf=mf,
        elec_potential_type=elec_potential_type,
        potential_value=potential_value,
        dual_potential_type=dual_potential_type,
        dual_potential_value=dual_potential_value,
        x_displacement_type=x_displacement_type,
        x_displacement_value=x_displacement_value,
        y_displacement_type=y_displacement_type,
        y_displacement_value=y_displacement_value,
        z_displacement_type=z_displacement_type,
        z_displacement_value=z_displacement_value,
        prob_mode_1=prob_mode_1,
        prob_mode_2=prob_mode_2,
        prob_mode_3=prob_mode_3,
        premixc=premixc,
        premixc_var=premixc_var,
        ecfm_sigma=ecfm_sigma,
        inert=inert,
        pollut_no=pollut_no,
        pollut_hcn=pollut_hcn,
        pollut_nh3=pollut_nh3,
        pollut_n2o=pollut_n2o,
        pollut_urea=pollut_urea,
        pollut_hnco=pollut_hnco,
        pollut_nco=pollut_nco,
        pollut_so2=pollut_so2,
        pollut_h2s=pollut_h2s,
        pollut_so3=pollut_so3,
        pollut_sh=pollut_sh,
        pollut_so=pollut_so,
        pollut_soot=pollut_soot,
        pollut_nuclei=pollut_nuclei,
        pollut_ctar=pollut_ctar,
        pollut_hg=pollut_hg,
        pollut_hgcl2=pollut_hgcl2,
        pollut_hcl=pollut_hcl,
        pollut_hgo=pollut_hgo,
        pollut_cl=pollut_cl,
        pollut_cl2=pollut_cl2,
        pollut_hgcl=pollut_hgcl,
        pollut_hocl=pollut_hocl,
        tss_scalar=tss_scalar,
        fensapice_flow_bc_subtype=fensapice_flow_bc_subtype,
        uds_bc=uds_bc,
        uds=uds,
        pb_disc_bc=pb_disc_bc,
        pb_disc=pb_disc,
        pb_qmom_bc=pb_qmom_bc,
        pb_qmom=pb_qmom,
        pb_smm_bc=pb_smm_bc,
        pb_smm=pb_smm,
        pb_dqmom_bc=pb_dqmom_bc,
        pb_dqmom=pb_dqmom,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        mixing_plane_thread=mixing_plane_thread,
        ac_options=ac_options,
        p_backflow_spec=p_backflow_spec,
        p_backflow_spec_gen=p_backflow_spec_gen,
        impedance_0=impedance_0,
        impedance_1=impedance_1,
        impedance_2=impedance_2,
        ac_wave=ac_wave,
        prevent_reverse_flow=prevent_reverse_flow,
        radial=radial,
        avg_press_spec=avg_press_spec,
        press_averaging_method=press_averaging_method,
        targeted_mf_boundary=targeted_mf_boundary,
        targeted_mf=targeted_mf,
        targeted_mf_pmax=targeted_mf_pmax,
        targeted_mf_pmin=targeted_mf_pmin,
        gen_nrbc_spec=gen_nrbc_spec,
        wsf=wsf,
        wsb=wsb,
        wsn=wsn,
        solar_fluxes=solar_fluxes,
        solar_shining_factor=solar_shining_factor,
        radiating_s2s_surface=radiating_s2s_surface,
        b=b,
        strength=strength,
    )
    return_type = 'object'

class phase_13(NamedObject[phase_13_child], CreatableNamedObjectMixinOld[phase_13_child]):
    """
    'phase' child.
    """
    _version = '222'
    fluent_name = 'phase'
    _python_name = 'phase'
    child_object_type = phase_13_child
    return_type = 'object'

class outlet_vent_child(Group):
    """
    'child_object_type' of outlet_vent.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'outlet_vent_child'
    child_names = ['phase', 'geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'open_channel', 'outlet_number', 'pressure_spec_method', 'press_spec', 'frame_of_reference', 'phase_spec', 'ht_local', 'p', 'p_profile_multiplier', 'ht_bottom', 'den_spec', 't0', 'direction_spec', 'coordinate_system', 'flow_direction_component', 'axis_direction_component', 'axis_origin_component', 'ke_spec', 'nut', 'kl', 'intermit', 'k', 'e', 'o', 'v2', 'turb_intensity', 'turb_length_scale', 'turb_hydraulic_diam', 'turb_viscosity_ratio', 'turb_viscosity_ratio_profile', 'rst_spec', 'uu', 'vv', 'ww', 'uv', 'vw', 'uw', 'ksgs_spec', 'ksgs', 'sgs_turb_intensity', 'radiation_bc', 'radial_direction_component', 'coll_dtheta', 'coll_dphi', 'band_q_irrad', 'band_q_irrad_diffuse', 'parallel_collimated_beam', 'solar_direction', 'solar_irradiation', 't_b_b_spec', 't_b_b', 'in_emiss', 'fmean', 'fmean2', 'fvar', 'fvar2', 'granular_temperature', 'iac', 'lsfun', 'vof_spec', 'volume_fraction', 'species_in_mole_fractions', 'mf', 'elec_potential_type', 'potential_value', 'dual_potential_type', 'dual_potential_value', 'x_displacement_type', 'x_displacement_value', 'y_displacement_type', 'y_displacement_value', 'z_displacement_type', 'z_displacement_value', 'prob_mode_1', 'prob_mode_2', 'prob_mode_3', 'premixc', 'premixc_var', 'ecfm_sigma', 'inert', 'pollut_no', 'pollut_hcn', 'pollut_nh3', 'pollut_n2o', 'pollut_urea', 'pollut_hnco', 'pollut_nco', 'pollut_so2', 'pollut_h2s', 'pollut_so3', 'pollut_sh', 'pollut_so', 'pollut_soot', 'pollut_nuclei', 'pollut_ctar', 'pollut_hg', 'pollut_hgcl2', 'pollut_hcl', 'pollut_hgo', 'pollut_cl', 'pollut_cl2', 'pollut_hgcl', 'pollut_hocl', 'tss_scalar', 'fensapice_flow_bc_subtype', 'uds_bc', 'uds', 'pb_disc_bc', 'pb_disc', 'pb_qmom_bc', 'pb_qmom', 'pb_smm_bc', 'pb_smm', 'pb_dqmom_bc', 'pb_dqmom', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'mixing_plane_thread', 'ac_options', 'p_backflow_spec', 'p_backflow_spec_gen', 'impedance_0', 'impedance_1', 'impedance_2', 'ac_wave', 'prevent_reverse_flow', 'radial', 'avg_press_spec', 'press_averaging_method', 'targeted_mf_boundary', 'targeted_mf', 'targeted_mf_pmax', 'targeted_mf_pmin', 'gen_nrbc_spec', 'wsf', 'wsb', 'wsn', 'solar_fluxes', 'solar_shining_factor', 'radiating_s2s_surface', 'b', 'strength']
    _child_classes = dict(
        phase=phase_13,
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        open_channel=open_channel,
        outlet_number=outlet_number,
        pressure_spec_method=pressure_spec_method,
        press_spec=press_spec,
        frame_of_reference=frame_of_reference,
        phase_spec=phase_spec,
        ht_local=ht_local,
        p=p,
        p_profile_multiplier=p_profile_multiplier,
        ht_bottom=ht_bottom,
        den_spec=den_spec,
        t0=t0,
        direction_spec=direction_spec,
        coordinate_system=coordinate_system,
        flow_direction_component=flow_direction_component,
        axis_direction_component=axis_direction_component_1,
        axis_origin_component=axis_origin_component_1,
        ke_spec=ke_spec,
        nut=nut,
        kl=kl,
        intermit=intermit,
        k=k,
        e=e,
        o=o,
        v2=v2,
        turb_intensity=turb_intensity,
        turb_length_scale=turb_length_scale,
        turb_hydraulic_diam=turb_hydraulic_diam,
        turb_viscosity_ratio=turb_viscosity_ratio,
        turb_viscosity_ratio_profile=turb_viscosity_ratio_profile,
        rst_spec=rst_spec,
        uu=uu,
        vv=vv,
        ww=ww,
        uv=uv,
        vw=vw,
        uw=uw,
        ksgs_spec=ksgs_spec,
        ksgs=ksgs,
        sgs_turb_intensity=sgs_turb_intensity,
        radiation_bc=radiation_bc,
        radial_direction_component=radial_direction_component,
        coll_dtheta=coll_dtheta,
        coll_dphi=coll_dphi,
        band_q_irrad=band_q_irrad,
        band_q_irrad_diffuse=band_q_irrad_diffuse,
        parallel_collimated_beam=parallel_collimated_beam,
        solar_direction=solar_direction,
        solar_irradiation=solar_irradiation,
        t_b_b_spec=t_b_b_spec,
        t_b_b=t_b_b,
        in_emiss=in_emiss,
        fmean=fmean,
        fmean2=fmean2,
        fvar=fvar,
        fvar2=fvar2,
        granular_temperature=granular_temperature,
        iac=iac,
        lsfun=lsfun,
        vof_spec=vof_spec,
        volume_fraction=volume_fraction,
        species_in_mole_fractions=species_in_mole_fractions,
        mf=mf,
        elec_potential_type=elec_potential_type,
        potential_value=potential_value,
        dual_potential_type=dual_potential_type,
        dual_potential_value=dual_potential_value,
        x_displacement_type=x_displacement_type,
        x_displacement_value=x_displacement_value,
        y_displacement_type=y_displacement_type,
        y_displacement_value=y_displacement_value,
        z_displacement_type=z_displacement_type,
        z_displacement_value=z_displacement_value,
        prob_mode_1=prob_mode_1,
        prob_mode_2=prob_mode_2,
        prob_mode_3=prob_mode_3,
        premixc=premixc,
        premixc_var=premixc_var,
        ecfm_sigma=ecfm_sigma,
        inert=inert,
        pollut_no=pollut_no,
        pollut_hcn=pollut_hcn,
        pollut_nh3=pollut_nh3,
        pollut_n2o=pollut_n2o,
        pollut_urea=pollut_urea,
        pollut_hnco=pollut_hnco,
        pollut_nco=pollut_nco,
        pollut_so2=pollut_so2,
        pollut_h2s=pollut_h2s,
        pollut_so3=pollut_so3,
        pollut_sh=pollut_sh,
        pollut_so=pollut_so,
        pollut_soot=pollut_soot,
        pollut_nuclei=pollut_nuclei,
        pollut_ctar=pollut_ctar,
        pollut_hg=pollut_hg,
        pollut_hgcl2=pollut_hgcl2,
        pollut_hcl=pollut_hcl,
        pollut_hgo=pollut_hgo,
        pollut_cl=pollut_cl,
        pollut_cl2=pollut_cl2,
        pollut_hgcl=pollut_hgcl,
        pollut_hocl=pollut_hocl,
        tss_scalar=tss_scalar,
        fensapice_flow_bc_subtype=fensapice_flow_bc_subtype,
        uds_bc=uds_bc,
        uds=uds,
        pb_disc_bc=pb_disc_bc,
        pb_disc=pb_disc,
        pb_qmom_bc=pb_qmom_bc,
        pb_qmom=pb_qmom,
        pb_smm_bc=pb_smm_bc,
        pb_smm=pb_smm,
        pb_dqmom_bc=pb_dqmom_bc,
        pb_dqmom=pb_dqmom,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        mixing_plane_thread=mixing_plane_thread,
        ac_options=ac_options,
        p_backflow_spec=p_backflow_spec,
        p_backflow_spec_gen=p_backflow_spec_gen,
        impedance_0=impedance_0,
        impedance_1=impedance_1,
        impedance_2=impedance_2,
        ac_wave=ac_wave,
        prevent_reverse_flow=prevent_reverse_flow,
        radial=radial,
        avg_press_spec=avg_press_spec,
        press_averaging_method=press_averaging_method,
        targeted_mf_boundary=targeted_mf_boundary,
        targeted_mf=targeted_mf,
        targeted_mf_pmax=targeted_mf_pmax,
        targeted_mf_pmin=targeted_mf_pmin,
        gen_nrbc_spec=gen_nrbc_spec,
        wsf=wsf,
        wsb=wsb,
        wsn=wsn,
        solar_fluxes=solar_fluxes,
        solar_shining_factor=solar_shining_factor,
        radiating_s2s_surface=radiating_s2s_surface,
        b=b,
        strength=strength,
    )
    return_type = 'object'

class outlet_vent(NamedObject[outlet_vent_child], CreatableNamedObjectMixinOld[outlet_vent_child]):
    """
    'outlet_vent' child.
    """
    _version = '222'
    fluent_name = 'outlet-vent'
    _python_name = 'outlet_vent'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = outlet_vent_child
    return_type = 'object'

class overset_child(Group):
    """
    'child_object_type' of overset.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'overset_child'
    child_names = ['phase', 'geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread']
    _child_classes = dict(
        phase=phase_2,
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
    )
    return_type = 'object'

class overset(NamedObject[overset_child], CreatableNamedObjectMixinOld[overset_child]):
    """
    'overset' child.
    """
    _version = '222'
    fluent_name = 'overset'
    _python_name = 'overset'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = overset_child
    return_type = 'object'

class angular(Boolean, AllowedValuesMixin):
    """
    'angular' child.
    """
    _version = '222'
    fluent_name = 'angular?'
    _python_name = 'angular'
    return_type = 'object'

class p_jump(Real, AllowedValuesMixin):
    """
    'p_jump' child.
    """
    _version = '222'
    fluent_name = 'p-jump'
    _python_name = 'p_jump'
    return_type = 'object'

class phase_14_child(Group):
    """
    'child_object_type' of phase.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'phase_child'
    child_names = ['geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'angular', 'p_jump']
    _child_classes = dict(
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        angular=angular,
        p_jump=p_jump,
    )
    return_type = 'object'

class phase_14(NamedObject[phase_14_child], CreatableNamedObjectMixinOld[phase_14_child]):
    """
    'phase' child.
    """
    _version = '222'
    fluent_name = 'phase'
    _python_name = 'phase'
    child_object_type = phase_14_child
    return_type = 'object'

class periodic_child(Group):
    """
    'child_object_type' of periodic.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'periodic_child'
    child_names = ['phase', 'geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'angular', 'p_jump']
    _child_classes = dict(
        phase=phase_14,
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        angular=angular,
        p_jump=p_jump,
    )
    return_type = 'object'

class periodic(NamedObject[periodic_child], CreatableNamedObjectMixinOld[periodic_child]):
    """
    'periodic' child.
    """
    _version = '222'
    fluent_name = 'periodic'
    _python_name = 'periodic'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = periodic_child
    return_type = 'object'

class alpha(Real, AllowedValuesMixin):
    """
    'alpha' child.
    """
    _version = '222'
    fluent_name = 'alpha'
    _python_name = 'alpha'
    return_type = 'object'

class dm(Real, AllowedValuesMixin):
    """
    'dm' child.
    """
    _version = '222'
    fluent_name = 'dm'
    _python_name = 'dm'
    return_type = 'object'

class c2(Real, AllowedValuesMixin):
    """
    'c2' child.
    """
    _version = '222'
    fluent_name = 'c2'
    _python_name = 'c2'
    return_type = 'object'

class thermal_ctk(Real, AllowedValuesMixin):
    """
    'thermal_ctk' child.
    """
    _version = '222'
    fluent_name = 'thermal-ctk'
    _python_name = 'thermal_ctk'
    return_type = 'object'

class v_absp(Group):
    """
    'v_absp' child.
    """
    _version = '222'
    fluent_name = 'v-absp'
    _python_name = 'v_absp'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class ir_absp(Group):
    """
    'ir_absp' child.
    """
    _version = '222'
    fluent_name = 'ir-absp'
    _python_name = 'ir_absp'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class ir_trans(Group):
    """
    'ir_trans' child.
    """
    _version = '222'
    fluent_name = 'ir-trans'
    _python_name = 'ir_trans'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class v_trans(Group):
    """
    'v_trans' child.
    """
    _version = '222'
    fluent_name = 'v-trans'
    _python_name = 'v_trans'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class jump_adhesion(Boolean, AllowedValuesMixin):
    """
    'jump_adhesion' child.
    """
    _version = '222'
    fluent_name = 'jump-adhesion?'
    _python_name = 'jump_adhesion'
    return_type = 'object'

class adhesion_constrained(Boolean, AllowedValuesMixin):
    """
    'adhesion_constrained' child.
    """
    _version = '222'
    fluent_name = 'adhesion-constrained?'
    _python_name = 'adhesion_constrained'
    return_type = 'object'

class adhesion_angle_child(Group):
    """
    'child_object_type' of adhesion_angle.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'adhesion_angle_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class adhesion_angle(NamedObject[adhesion_angle_child], CreatableNamedObjectMixinOld[adhesion_angle_child]):
    """
    'adhesion_angle' child.
    """
    _version = '222'
    fluent_name = 'adhesion-angle'
    _python_name = 'adhesion_angle'
    child_object_type = adhesion_angle_child
    return_type = 'object'

class phase_15_child(Group):
    """
    'child_object_type' of phase.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'phase_child'
    child_names = ['geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'porous_jump_turb_wall_treatment', 'alpha', 'dm', 'c2', 'thermal_ctk', 'solar_fluxes', 'v_absp', 'ir_absp', 'ir_trans', 'v_trans', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'strength', 'jump_adhesion', 'adhesion_constrained', 'adhesion_angle', 'x_displacement_type', 'x_displacement_value', 'y_displacement_type', 'y_displacement_value', 'z_displacement_type', 'z_displacement_value']
    _child_classes = dict(
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        porous_jump_turb_wall_treatment=porous_jump_turb_wall_treatment,
        alpha=alpha,
        dm=dm,
        c2=c2,
        thermal_ctk=thermal_ctk,
        solar_fluxes=solar_fluxes,
        v_absp=v_absp,
        ir_absp=ir_absp,
        ir_trans=ir_trans,
        v_trans=v_trans,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        strength=strength,
        jump_adhesion=jump_adhesion,
        adhesion_constrained=adhesion_constrained,
        adhesion_angle=adhesion_angle,
        x_displacement_type=x_displacement_type,
        x_displacement_value=x_displacement_value,
        y_displacement_type=y_displacement_type,
        y_displacement_value=y_displacement_value,
        z_displacement_type=z_displacement_type,
        z_displacement_value=z_displacement_value,
    )
    return_type = 'object'

class phase_15(NamedObject[phase_15_child], CreatableNamedObjectMixinOld[phase_15_child]):
    """
    'phase' child.
    """
    _version = '222'
    fluent_name = 'phase'
    _python_name = 'phase'
    child_object_type = phase_15_child
    return_type = 'object'

class porous_jump_child(Group):
    """
    'child_object_type' of porous_jump.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'porous_jump_child'
    child_names = ['phase', 'geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'porous_jump_turb_wall_treatment', 'alpha', 'dm', 'c2', 'thermal_ctk', 'solar_fluxes', 'v_absp', 'ir_absp', 'ir_trans', 'v_trans', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'strength', 'jump_adhesion', 'adhesion_constrained', 'adhesion_angle', 'x_displacement_type', 'x_displacement_value', 'y_displacement_type', 'y_displacement_value', 'z_displacement_type', 'z_displacement_value']
    _child_classes = dict(
        phase=phase_15,
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        porous_jump_turb_wall_treatment=porous_jump_turb_wall_treatment,
        alpha=alpha,
        dm=dm,
        c2=c2,
        thermal_ctk=thermal_ctk,
        solar_fluxes=solar_fluxes,
        v_absp=v_absp,
        ir_absp=ir_absp,
        ir_trans=ir_trans,
        v_trans=v_trans,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        strength=strength,
        jump_adhesion=jump_adhesion,
        adhesion_constrained=adhesion_constrained,
        adhesion_angle=adhesion_angle,
        x_displacement_type=x_displacement_type,
        x_displacement_value=x_displacement_value,
        y_displacement_type=y_displacement_type,
        y_displacement_value=y_displacement_value,
        z_displacement_type=z_displacement_type,
        z_displacement_value=z_displacement_value,
    )
    return_type = 'object'

class porous_jump(NamedObject[porous_jump_child], CreatableNamedObjectMixinOld[porous_jump_child]):
    """
    'porous_jump' child.
    """
    _version = '222'
    fluent_name = 'porous-jump'
    _python_name = 'porous_jump'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = porous_jump_child
    return_type = 'object'

class m(Group):
    """
    'm' child.
    """
    _version = '222'
    fluent_name = 'm'
    _python_name = 'm'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class t(Group):
    """
    't' child.
    """
    _version = '222'
    fluent_name = 't'
    _python_name = 't'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class non_equil_boundary(Boolean, AllowedValuesMixin):
    """
    'non_equil_boundary' child.
    """
    _version = '222'
    fluent_name = 'non-equil-boundary?'
    _python_name = 'non_equil_boundary'
    return_type = 'object'

class tve(Group):
    """
    'tve' child.
    """
    _version = '222'
    fluent_name = 'tve'
    _python_name = 'tve'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class ni_1(Group):
    """
    'ni' child.
    """
    _version = '222'
    fluent_name = 'ni'
    _python_name = 'ni'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class nj_1(Group):
    """
    'nj' child.
    """
    _version = '222'
    fluent_name = 'nj'
    _python_name = 'nj'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class nk_1(Group):
    """
    'nk' child.
    """
    _version = '222'
    fluent_name = 'nk'
    _python_name = 'nk'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class phase_16_child(Group):
    """
    'child_object_type' of phase.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'phase_child'
    child_names = ['geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'p', 'm', 't', 'non_equil_boundary', 'tve', 'coordinate_system', 'ni', 'nj', 'nk', 'flow_direction_component', 'axis_direction_component', 'axis_origin_component', 'ke_spec', 'nut', 'kl', 'intermit', 'k', 'e', 'o', 'v2', 'turb_intensity', 'turb_length_scale', 'turb_hydraulic_diam', 'turb_viscosity_ratio', 'turb_viscosity_ratio_profile', 'rst_spec', 'uu', 'vv', 'ww', 'uv', 'vw', 'uw', 'ksgs_spec', 'ksgs', 'sgs_turb_intensity', 'radiation_bc', 'radial_direction_component', 'coll_dtheta', 'coll_dphi', 'band_q_irrad', 'band_q_irrad_diffuse', 'parallel_collimated_beam', 'solar_direction', 'solar_irradiation', 't_b_b_spec', 't_b_b', 'in_emiss', 'fmean', 'fvar', 'fmean2', 'fvar2', 'species_in_mole_fractions', 'mf', 'elec_potential_type', 'potential_value', 'dual_potential_type', 'dual_potential_value', 'x_displacement_type', 'x_displacement_value', 'y_displacement_type', 'y_displacement_value', 'z_displacement_type', 'z_displacement_value', 'prob_mode_1', 'prob_mode_2', 'prob_mode_3', 'pollut_no', 'pollut_hcn', 'pollut_nh3', 'pollut_n2o', 'pollut_urea', 'pollut_hnco', 'pollut_nco', 'pollut_so2', 'pollut_h2s', 'pollut_so3', 'pollut_sh', 'pollut_so', 'pollut_soot', 'pollut_nuclei', 'pollut_ctar', 'pollut_hg', 'pollut_hgcl2', 'pollut_hcl', 'pollut_hgo', 'pollut_cl', 'pollut_cl2', 'pollut_hgcl', 'pollut_hocl', 'fensapice_flow_bc_subtype', 'fensapice_drop_bccustom', 'fensapice_drop_lwc', 'fensapice_drop_dtemp', 'fensapice_drop_ddiam', 'fensapice_drop_dv', 'fensapice_drop_dx', 'fensapice_drop_dy', 'fensapice_drop_dz', 'fensapice_dpm_surface_injection', 'fensapice_dpm_inj_nstream', 'fensapice_drop_icc', 'fensapice_drop_ctemp', 'fensapice_drop_cdiam', 'fensapice_drop_cv', 'fensapice_drop_cx', 'fensapice_drop_cy', 'fensapice_drop_cz', 'fensapice_drop_vrh', 'fensapice_drop_vrh_1', 'fensapice_drop_vc', 'uds_bc', 'uds', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'solar_fluxes', 'solar_shining_factor', 'radiating_s2s_surface']
    _child_classes = dict(
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        p=p,
        m=m,
        t=t,
        non_equil_boundary=non_equil_boundary,
        tve=tve,
        coordinate_system=coordinate_system,
        ni=ni_1,
        nj=nj_1,
        nk=nk_1,
        flow_direction_component=flow_direction_component,
        axis_direction_component=axis_direction_component_1,
        axis_origin_component=axis_origin_component_1,
        ke_spec=ke_spec,
        nut=nut,
        kl=kl,
        intermit=intermit,
        k=k,
        e=e,
        o=o,
        v2=v2,
        turb_intensity=turb_intensity,
        turb_length_scale=turb_length_scale,
        turb_hydraulic_diam=turb_hydraulic_diam,
        turb_viscosity_ratio=turb_viscosity_ratio,
        turb_viscosity_ratio_profile=turb_viscosity_ratio_profile,
        rst_spec=rst_spec,
        uu=uu,
        vv=vv,
        ww=ww,
        uv=uv,
        vw=vw,
        uw=uw,
        ksgs_spec=ksgs_spec,
        ksgs=ksgs,
        sgs_turb_intensity=sgs_turb_intensity,
        radiation_bc=radiation_bc,
        radial_direction_component=radial_direction_component,
        coll_dtheta=coll_dtheta,
        coll_dphi=coll_dphi,
        band_q_irrad=band_q_irrad,
        band_q_irrad_diffuse=band_q_irrad_diffuse,
        parallel_collimated_beam=parallel_collimated_beam,
        solar_direction=solar_direction,
        solar_irradiation=solar_irradiation,
        t_b_b_spec=t_b_b_spec,
        t_b_b=t_b_b,
        in_emiss=in_emiss,
        fmean=fmean,
        fvar=fvar,
        fmean2=fmean2,
        fvar2=fvar2,
        species_in_mole_fractions=species_in_mole_fractions,
        mf=mf,
        elec_potential_type=elec_potential_type,
        potential_value=potential_value,
        dual_potential_type=dual_potential_type,
        dual_potential_value=dual_potential_value,
        x_displacement_type=x_displacement_type,
        x_displacement_value=x_displacement_value,
        y_displacement_type=y_displacement_type,
        y_displacement_value=y_displacement_value,
        z_displacement_type=z_displacement_type,
        z_displacement_value=z_displacement_value,
        prob_mode_1=prob_mode_1,
        prob_mode_2=prob_mode_2,
        prob_mode_3=prob_mode_3,
        pollut_no=pollut_no,
        pollut_hcn=pollut_hcn,
        pollut_nh3=pollut_nh3,
        pollut_n2o=pollut_n2o,
        pollut_urea=pollut_urea,
        pollut_hnco=pollut_hnco,
        pollut_nco=pollut_nco,
        pollut_so2=pollut_so2,
        pollut_h2s=pollut_h2s,
        pollut_so3=pollut_so3,
        pollut_sh=pollut_sh,
        pollut_so=pollut_so,
        pollut_soot=pollut_soot,
        pollut_nuclei=pollut_nuclei,
        pollut_ctar=pollut_ctar,
        pollut_hg=pollut_hg,
        pollut_hgcl2=pollut_hgcl2,
        pollut_hcl=pollut_hcl,
        pollut_hgo=pollut_hgo,
        pollut_cl=pollut_cl,
        pollut_cl2=pollut_cl2,
        pollut_hgcl=pollut_hgcl,
        pollut_hocl=pollut_hocl,
        fensapice_flow_bc_subtype=fensapice_flow_bc_subtype,
        fensapice_drop_bccustom=fensapice_drop_bccustom,
        fensapice_drop_lwc=fensapice_drop_lwc,
        fensapice_drop_dtemp=fensapice_drop_dtemp,
        fensapice_drop_ddiam=fensapice_drop_ddiam,
        fensapice_drop_dv=fensapice_drop_dv,
        fensapice_drop_dx=fensapice_drop_dx,
        fensapice_drop_dy=fensapice_drop_dy,
        fensapice_drop_dz=fensapice_drop_dz,
        fensapice_dpm_surface_injection=fensapice_dpm_surface_injection,
        fensapice_dpm_inj_nstream=fensapice_dpm_inj_nstream,
        fensapice_drop_icc=fensapice_drop_icc,
        fensapice_drop_ctemp=fensapice_drop_ctemp,
        fensapice_drop_cdiam=fensapice_drop_cdiam,
        fensapice_drop_cv=fensapice_drop_cv,
        fensapice_drop_cx=fensapice_drop_cx,
        fensapice_drop_cy=fensapice_drop_cy,
        fensapice_drop_cz=fensapice_drop_cz,
        fensapice_drop_vrh=fensapice_drop_vrh,
        fensapice_drop_vrh_1=fensapice_drop_vrh_1,
        fensapice_drop_vc=fensapice_drop_vc,
        uds_bc=uds_bc,
        uds=uds,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        solar_fluxes=solar_fluxes,
        solar_shining_factor=solar_shining_factor,
        radiating_s2s_surface=radiating_s2s_surface,
    )
    return_type = 'object'

class phase_16(NamedObject[phase_16_child], CreatableNamedObjectMixinOld[phase_16_child]):
    """
    'phase' child.
    """
    _version = '222'
    fluent_name = 'phase'
    _python_name = 'phase'
    child_object_type = phase_16_child
    return_type = 'object'

class pressure_far_field_child(Group):
    """
    'child_object_type' of pressure_far_field.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'pressure_far_field_child'
    child_names = ['phase', 'geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'p', 'm', 't', 'non_equil_boundary', 'tve', 'coordinate_system', 'ni', 'nj', 'nk', 'flow_direction_component', 'axis_direction_component', 'axis_origin_component', 'ke_spec', 'nut', 'kl', 'intermit', 'k', 'e', 'o', 'v2', 'turb_intensity', 'turb_length_scale', 'turb_hydraulic_diam', 'turb_viscosity_ratio', 'turb_viscosity_ratio_profile', 'rst_spec', 'uu', 'vv', 'ww', 'uv', 'vw', 'uw', 'ksgs_spec', 'ksgs', 'sgs_turb_intensity', 'radiation_bc', 'radial_direction_component', 'coll_dtheta', 'coll_dphi', 'band_q_irrad', 'band_q_irrad_diffuse', 'parallel_collimated_beam', 'solar_direction', 'solar_irradiation', 't_b_b_spec', 't_b_b', 'in_emiss', 'fmean', 'fvar', 'fmean2', 'fvar2', 'species_in_mole_fractions', 'mf', 'elec_potential_type', 'potential_value', 'dual_potential_type', 'dual_potential_value', 'x_displacement_type', 'x_displacement_value', 'y_displacement_type', 'y_displacement_value', 'z_displacement_type', 'z_displacement_value', 'prob_mode_1', 'prob_mode_2', 'prob_mode_3', 'pollut_no', 'pollut_hcn', 'pollut_nh3', 'pollut_n2o', 'pollut_urea', 'pollut_hnco', 'pollut_nco', 'pollut_so2', 'pollut_h2s', 'pollut_so3', 'pollut_sh', 'pollut_so', 'pollut_soot', 'pollut_nuclei', 'pollut_ctar', 'pollut_hg', 'pollut_hgcl2', 'pollut_hcl', 'pollut_hgo', 'pollut_cl', 'pollut_cl2', 'pollut_hgcl', 'pollut_hocl', 'fensapice_flow_bc_subtype', 'fensapice_drop_bccustom', 'fensapice_drop_lwc', 'fensapice_drop_dtemp', 'fensapice_drop_ddiam', 'fensapice_drop_dv', 'fensapice_drop_dx', 'fensapice_drop_dy', 'fensapice_drop_dz', 'fensapice_dpm_surface_injection', 'fensapice_dpm_inj_nstream', 'fensapice_drop_icc', 'fensapice_drop_ctemp', 'fensapice_drop_cdiam', 'fensapice_drop_cv', 'fensapice_drop_cx', 'fensapice_drop_cy', 'fensapice_drop_cz', 'fensapice_drop_vrh', 'fensapice_drop_vrh_1', 'fensapice_drop_vc', 'uds_bc', 'uds', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'solar_fluxes', 'solar_shining_factor', 'radiating_s2s_surface']
    _child_classes = dict(
        phase=phase_16,
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        p=p,
        m=m,
        t=t,
        non_equil_boundary=non_equil_boundary,
        tve=tve,
        coordinate_system=coordinate_system,
        ni=ni_1,
        nj=nj_1,
        nk=nk_1,
        flow_direction_component=flow_direction_component,
        axis_direction_component=axis_direction_component_1,
        axis_origin_component=axis_origin_component_1,
        ke_spec=ke_spec,
        nut=nut,
        kl=kl,
        intermit=intermit,
        k=k,
        e=e,
        o=o,
        v2=v2,
        turb_intensity=turb_intensity,
        turb_length_scale=turb_length_scale,
        turb_hydraulic_diam=turb_hydraulic_diam,
        turb_viscosity_ratio=turb_viscosity_ratio,
        turb_viscosity_ratio_profile=turb_viscosity_ratio_profile,
        rst_spec=rst_spec,
        uu=uu,
        vv=vv,
        ww=ww,
        uv=uv,
        vw=vw,
        uw=uw,
        ksgs_spec=ksgs_spec,
        ksgs=ksgs,
        sgs_turb_intensity=sgs_turb_intensity,
        radiation_bc=radiation_bc,
        radial_direction_component=radial_direction_component,
        coll_dtheta=coll_dtheta,
        coll_dphi=coll_dphi,
        band_q_irrad=band_q_irrad,
        band_q_irrad_diffuse=band_q_irrad_diffuse,
        parallel_collimated_beam=parallel_collimated_beam,
        solar_direction=solar_direction,
        solar_irradiation=solar_irradiation,
        t_b_b_spec=t_b_b_spec,
        t_b_b=t_b_b,
        in_emiss=in_emiss,
        fmean=fmean,
        fvar=fvar,
        fmean2=fmean2,
        fvar2=fvar2,
        species_in_mole_fractions=species_in_mole_fractions,
        mf=mf,
        elec_potential_type=elec_potential_type,
        potential_value=potential_value,
        dual_potential_type=dual_potential_type,
        dual_potential_value=dual_potential_value,
        x_displacement_type=x_displacement_type,
        x_displacement_value=x_displacement_value,
        y_displacement_type=y_displacement_type,
        y_displacement_value=y_displacement_value,
        z_displacement_type=z_displacement_type,
        z_displacement_value=z_displacement_value,
        prob_mode_1=prob_mode_1,
        prob_mode_2=prob_mode_2,
        prob_mode_3=prob_mode_3,
        pollut_no=pollut_no,
        pollut_hcn=pollut_hcn,
        pollut_nh3=pollut_nh3,
        pollut_n2o=pollut_n2o,
        pollut_urea=pollut_urea,
        pollut_hnco=pollut_hnco,
        pollut_nco=pollut_nco,
        pollut_so2=pollut_so2,
        pollut_h2s=pollut_h2s,
        pollut_so3=pollut_so3,
        pollut_sh=pollut_sh,
        pollut_so=pollut_so,
        pollut_soot=pollut_soot,
        pollut_nuclei=pollut_nuclei,
        pollut_ctar=pollut_ctar,
        pollut_hg=pollut_hg,
        pollut_hgcl2=pollut_hgcl2,
        pollut_hcl=pollut_hcl,
        pollut_hgo=pollut_hgo,
        pollut_cl=pollut_cl,
        pollut_cl2=pollut_cl2,
        pollut_hgcl=pollut_hgcl,
        pollut_hocl=pollut_hocl,
        fensapice_flow_bc_subtype=fensapice_flow_bc_subtype,
        fensapice_drop_bccustom=fensapice_drop_bccustom,
        fensapice_drop_lwc=fensapice_drop_lwc,
        fensapice_drop_dtemp=fensapice_drop_dtemp,
        fensapice_drop_ddiam=fensapice_drop_ddiam,
        fensapice_drop_dv=fensapice_drop_dv,
        fensapice_drop_dx=fensapice_drop_dx,
        fensapice_drop_dy=fensapice_drop_dy,
        fensapice_drop_dz=fensapice_drop_dz,
        fensapice_dpm_surface_injection=fensapice_dpm_surface_injection,
        fensapice_dpm_inj_nstream=fensapice_dpm_inj_nstream,
        fensapice_drop_icc=fensapice_drop_icc,
        fensapice_drop_ctemp=fensapice_drop_ctemp,
        fensapice_drop_cdiam=fensapice_drop_cdiam,
        fensapice_drop_cv=fensapice_drop_cv,
        fensapice_drop_cx=fensapice_drop_cx,
        fensapice_drop_cy=fensapice_drop_cy,
        fensapice_drop_cz=fensapice_drop_cz,
        fensapice_drop_vrh=fensapice_drop_vrh,
        fensapice_drop_vrh_1=fensapice_drop_vrh_1,
        fensapice_drop_vc=fensapice_drop_vc,
        uds_bc=uds_bc,
        uds=uds,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        solar_fluxes=solar_fluxes,
        solar_shining_factor=solar_shining_factor,
        radiating_s2s_surface=radiating_s2s_surface,
    )
    return_type = 'object'

class pressure_far_field(NamedObject[pressure_far_field_child], CreatableNamedObjectMixinOld[pressure_far_field_child]):
    """
    'pressure_far_field' child.
    """
    _version = '222'
    fluent_name = 'pressure-far-field'
    _python_name = 'pressure_far_field'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = pressure_far_field_child
    return_type = 'object'

class phase_17_child(Group):
    """
    'child_object_type' of phase.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'phase_child'
    child_names = ['geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'open_channel', 'inlet_number', 'phase_spec', 'frame_of_reference', 'p0', 'supersonic_or_initial_gauge_pressure', 't0', 'direction_spec', 'flow_spec', 'ht_local', 'ht_total', 'vmag', 'ht_bottom', 'den_spec', 'coordinate_system', 'flow_direction_component', 'direction_vector_components', 'axis_direction_component', 'axis_origin_component', 'les_spec_name', 'rfg_number_of_modes', 'vm_number_of_vortices', 'vm_streamwise_fluct', 'vm_mass_conservation', 'volumetric_synthetic_turbulence_generator', 'volumetric_synthetic_turbulence_generator_option', 'volumetric_synthetic_turbulence_generator_option_thickness', 'prevent_reverse_flow', 'ke_spec', 'nut', 'kl', 'intermit', 'k', 'e', 'o', 'v2', 'turb_intensity', 'turb_length_scale', 'turb_hydraulic_diam', 'turb_viscosity_ratio', 'turb_viscosity_ratio_profile', 'rst_spec', 'uu', 'vv', 'ww', 'uv', 'vw', 'uw', 'ksgs_spec', 'ksgs', 'sgs_turb_intensity', 'granular_temperature', 'iac', 'lsfun', 'volume_fraction', 'species_in_mole_fractions', 'mf', 'elec_potential_type', 'potential_value', 'dual_potential_type', 'dual_potential_value', 'x_displacement_type', 'x_displacement_value', 'y_displacement_type', 'y_displacement_value', 'z_displacement_type', 'z_displacement_value', 'prob_mode_1', 'prob_mode_2', 'prob_mode_3', 'equ_required', 'uds_bc', 'uds', 'pb_disc_bc', 'pb_disc', 'pb_qmom_bc', 'pb_qmom', 'pb_smm_bc', 'pb_smm', 'pb_dqmom_bc', 'pb_dqmom', 'radiation_bc', 'radial_direction_component', 'coll_dtheta', 'coll_dphi', 'band_q_irrad', 'band_q_irrad_diffuse', 'parallel_collimated_beam', 'solar_direction', 'solar_irradiation', 't_b_b_spec', 't_b_b', 'in_emiss', 'fmean', 'fvar', 'fmean2', 'fvar2', 'premixc', 'premixc_var', 'ecfm_sigma', 'inert', 'pollut_no', 'pollut_hcn', 'pollut_nh3', 'pollut_n2o', 'pollut_urea', 'pollut_hnco', 'pollut_nco', 'pollut_so2', 'pollut_h2s', 'pollut_so3', 'pollut_sh', 'pollut_so', 'pollut_soot', 'pollut_nuclei', 'pollut_ctar', 'pollut_hg', 'pollut_hgcl2', 'pollut_hcl', 'pollut_hgo', 'pollut_cl', 'pollut_cl2', 'pollut_hgcl', 'pollut_hocl', 'tss_scalar', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'fensapice_flow_bc_subtype', 'fensapice_drop_bccustom', 'fensapice_drop_lwc', 'fensapice_drop_dtemp', 'fensapice_drop_ddiam', 'fensapice_drop_dv', 'fensapice_drop_dx', 'fensapice_drop_dy', 'fensapice_drop_dz', 'fensapice_dpm_surface_injection', 'fensapice_dpm_inj_nstream', 'fensapice_drop_icc', 'fensapice_drop_ctemp', 'fensapice_drop_cdiam', 'fensapice_drop_cv', 'fensapice_drop_cx', 'fensapice_drop_cy', 'fensapice_drop_cz', 'fensapice_drop_vrh', 'fensapice_drop_vrh_1', 'fensapice_drop_vc', 'mixing_plane_thread', 'wsf', 'wsb', 'wsn', 'solar_fluxes', 'solar_shining_factor', 'radiating_s2s_surface', 'ac_options', 'impedance_0', 'impedance_1', 'impedance_2', 'ac_wave', 'les_spec']
    _child_classes = dict(
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        open_channel=open_channel,
        inlet_number=inlet_number,
        phase_spec=phase_spec,
        frame_of_reference=frame_of_reference,
        p0=p0,
        supersonic_or_initial_gauge_pressure=supersonic_or_initial_gauge_pressure,
        t0=t0,
        direction_spec=direction_spec,
        flow_spec=flow_spec,
        ht_local=ht_local,
        ht_total=ht_total,
        vmag=vmag,
        ht_bottom=ht_bottom,
        den_spec=den_spec,
        coordinate_system=coordinate_system,
        flow_direction_component=flow_direction_component,
        direction_vector_components=direction_vector_components,
        axis_direction_component=axis_direction_component_1,
        axis_origin_component=axis_origin_component_1,
        les_spec_name=les_spec_name,
        rfg_number_of_modes=rfg_number_of_modes,
        vm_number_of_vortices=vm_number_of_vortices,
        vm_streamwise_fluct=vm_streamwise_fluct,
        vm_mass_conservation=vm_mass_conservation,
        volumetric_synthetic_turbulence_generator=volumetric_synthetic_turbulence_generator,
        volumetric_synthetic_turbulence_generator_option=volumetric_synthetic_turbulence_generator_option,
        volumetric_synthetic_turbulence_generator_option_thickness=volumetric_synthetic_turbulence_generator_option_thickness,
        prevent_reverse_flow=prevent_reverse_flow,
        ke_spec=ke_spec,
        nut=nut,
        kl=kl,
        intermit=intermit,
        k=k,
        e=e,
        o=o,
        v2=v2,
        turb_intensity=turb_intensity,
        turb_length_scale=turb_length_scale,
        turb_hydraulic_diam=turb_hydraulic_diam,
        turb_viscosity_ratio=turb_viscosity_ratio,
        turb_viscosity_ratio_profile=turb_viscosity_ratio_profile,
        rst_spec=rst_spec,
        uu=uu,
        vv=vv,
        ww=ww,
        uv=uv,
        vw=vw,
        uw=uw,
        ksgs_spec=ksgs_spec,
        ksgs=ksgs,
        sgs_turb_intensity=sgs_turb_intensity,
        granular_temperature=granular_temperature,
        iac=iac,
        lsfun=lsfun,
        volume_fraction=volume_fraction,
        species_in_mole_fractions=species_in_mole_fractions,
        mf=mf,
        elec_potential_type=elec_potential_type,
        potential_value=potential_value,
        dual_potential_type=dual_potential_type,
        dual_potential_value=dual_potential_value,
        x_displacement_type=x_displacement_type,
        x_displacement_value=x_displacement_value,
        y_displacement_type=y_displacement_type,
        y_displacement_value=y_displacement_value,
        z_displacement_type=z_displacement_type,
        z_displacement_value=z_displacement_value,
        prob_mode_1=prob_mode_1,
        prob_mode_2=prob_mode_2,
        prob_mode_3=prob_mode_3,
        equ_required=equ_required,
        uds_bc=uds_bc,
        uds=uds,
        pb_disc_bc=pb_disc_bc,
        pb_disc=pb_disc,
        pb_qmom_bc=pb_qmom_bc,
        pb_qmom=pb_qmom,
        pb_smm_bc=pb_smm_bc,
        pb_smm=pb_smm,
        pb_dqmom_bc=pb_dqmom_bc,
        pb_dqmom=pb_dqmom,
        radiation_bc=radiation_bc,
        radial_direction_component=radial_direction_component,
        coll_dtheta=coll_dtheta,
        coll_dphi=coll_dphi,
        band_q_irrad=band_q_irrad,
        band_q_irrad_diffuse=band_q_irrad_diffuse,
        parallel_collimated_beam=parallel_collimated_beam,
        solar_direction=solar_direction,
        solar_irradiation=solar_irradiation,
        t_b_b_spec=t_b_b_spec,
        t_b_b=t_b_b,
        in_emiss=in_emiss,
        fmean=fmean,
        fvar=fvar,
        fmean2=fmean2,
        fvar2=fvar2,
        premixc=premixc,
        premixc_var=premixc_var,
        ecfm_sigma=ecfm_sigma,
        inert=inert,
        pollut_no=pollut_no,
        pollut_hcn=pollut_hcn,
        pollut_nh3=pollut_nh3,
        pollut_n2o=pollut_n2o,
        pollut_urea=pollut_urea,
        pollut_hnco=pollut_hnco,
        pollut_nco=pollut_nco,
        pollut_so2=pollut_so2,
        pollut_h2s=pollut_h2s,
        pollut_so3=pollut_so3,
        pollut_sh=pollut_sh,
        pollut_so=pollut_so,
        pollut_soot=pollut_soot,
        pollut_nuclei=pollut_nuclei,
        pollut_ctar=pollut_ctar,
        pollut_hg=pollut_hg,
        pollut_hgcl2=pollut_hgcl2,
        pollut_hcl=pollut_hcl,
        pollut_hgo=pollut_hgo,
        pollut_cl=pollut_cl,
        pollut_cl2=pollut_cl2,
        pollut_hgcl=pollut_hgcl,
        pollut_hocl=pollut_hocl,
        tss_scalar=tss_scalar,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        fensapice_flow_bc_subtype=fensapice_flow_bc_subtype,
        fensapice_drop_bccustom=fensapice_drop_bccustom,
        fensapice_drop_lwc=fensapice_drop_lwc,
        fensapice_drop_dtemp=fensapice_drop_dtemp,
        fensapice_drop_ddiam=fensapice_drop_ddiam,
        fensapice_drop_dv=fensapice_drop_dv,
        fensapice_drop_dx=fensapice_drop_dx,
        fensapice_drop_dy=fensapice_drop_dy,
        fensapice_drop_dz=fensapice_drop_dz,
        fensapice_dpm_surface_injection=fensapice_dpm_surface_injection,
        fensapice_dpm_inj_nstream=fensapice_dpm_inj_nstream,
        fensapice_drop_icc=fensapice_drop_icc,
        fensapice_drop_ctemp=fensapice_drop_ctemp,
        fensapice_drop_cdiam=fensapice_drop_cdiam,
        fensapice_drop_cv=fensapice_drop_cv,
        fensapice_drop_cx=fensapice_drop_cx,
        fensapice_drop_cy=fensapice_drop_cy,
        fensapice_drop_cz=fensapice_drop_cz,
        fensapice_drop_vrh=fensapice_drop_vrh,
        fensapice_drop_vrh_1=fensapice_drop_vrh_1,
        fensapice_drop_vc=fensapice_drop_vc,
        mixing_plane_thread=mixing_plane_thread,
        wsf=wsf,
        wsb=wsb,
        wsn=wsn,
        solar_fluxes=solar_fluxes,
        solar_shining_factor=solar_shining_factor,
        radiating_s2s_surface=radiating_s2s_surface,
        ac_options=ac_options,
        impedance_0=impedance_0,
        impedance_1=impedance_1,
        impedance_2=impedance_2,
        ac_wave=ac_wave,
        les_spec=les_spec,
    )
    return_type = 'object'

class phase_17(NamedObject[phase_17_child], CreatableNamedObjectMixinOld[phase_17_child]):
    """
    'phase' child.
    """
    _version = '222'
    fluent_name = 'phase'
    _python_name = 'phase'
    child_object_type = phase_17_child
    return_type = 'object'

class pressure_inlet_child(Group):
    """
    'child_object_type' of pressure_inlet.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'pressure_inlet_child'
    child_names = ['phase', 'geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'open_channel', 'inlet_number', 'phase_spec', 'frame_of_reference', 'p0', 'supersonic_or_initial_gauge_pressure', 't0', 'direction_spec', 'flow_spec', 'ht_local', 'ht_total', 'vmag', 'ht_bottom', 'den_spec', 'coordinate_system', 'flow_direction_component', 'direction_vector_components', 'axis_direction_component', 'axis_origin_component', 'les_spec_name', 'rfg_number_of_modes', 'vm_number_of_vortices', 'vm_streamwise_fluct', 'vm_mass_conservation', 'volumetric_synthetic_turbulence_generator', 'volumetric_synthetic_turbulence_generator_option', 'volumetric_synthetic_turbulence_generator_option_thickness', 'prevent_reverse_flow', 'ke_spec', 'nut', 'kl', 'intermit', 'k', 'e', 'o', 'v2', 'turb_intensity', 'turb_length_scale', 'turb_hydraulic_diam', 'turb_viscosity_ratio', 'turb_viscosity_ratio_profile', 'rst_spec', 'uu', 'vv', 'ww', 'uv', 'vw', 'uw', 'ksgs_spec', 'ksgs', 'sgs_turb_intensity', 'granular_temperature', 'iac', 'lsfun', 'volume_fraction', 'species_in_mole_fractions', 'mf', 'elec_potential_type', 'potential_value', 'dual_potential_type', 'dual_potential_value', 'x_displacement_type', 'x_displacement_value', 'y_displacement_type', 'y_displacement_value', 'z_displacement_type', 'z_displacement_value', 'prob_mode_1', 'prob_mode_2', 'prob_mode_3', 'equ_required', 'uds_bc', 'uds', 'pb_disc_bc', 'pb_disc', 'pb_qmom_bc', 'pb_qmom', 'pb_smm_bc', 'pb_smm', 'pb_dqmom_bc', 'pb_dqmom', 'radiation_bc', 'radial_direction_component', 'coll_dtheta', 'coll_dphi', 'band_q_irrad', 'band_q_irrad_diffuse', 'parallel_collimated_beam', 'solar_direction', 'solar_irradiation', 't_b_b_spec', 't_b_b', 'in_emiss', 'fmean', 'fvar', 'fmean2', 'fvar2', 'premixc', 'premixc_var', 'ecfm_sigma', 'inert', 'pollut_no', 'pollut_hcn', 'pollut_nh3', 'pollut_n2o', 'pollut_urea', 'pollut_hnco', 'pollut_nco', 'pollut_so2', 'pollut_h2s', 'pollut_so3', 'pollut_sh', 'pollut_so', 'pollut_soot', 'pollut_nuclei', 'pollut_ctar', 'pollut_hg', 'pollut_hgcl2', 'pollut_hcl', 'pollut_hgo', 'pollut_cl', 'pollut_cl2', 'pollut_hgcl', 'pollut_hocl', 'tss_scalar', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'fensapice_flow_bc_subtype', 'fensapice_drop_bccustom', 'fensapice_drop_lwc', 'fensapice_drop_dtemp', 'fensapice_drop_ddiam', 'fensapice_drop_dv', 'fensapice_drop_dx', 'fensapice_drop_dy', 'fensapice_drop_dz', 'fensapice_dpm_surface_injection', 'fensapice_dpm_inj_nstream', 'fensapice_drop_icc', 'fensapice_drop_ctemp', 'fensapice_drop_cdiam', 'fensapice_drop_cv', 'fensapice_drop_cx', 'fensapice_drop_cy', 'fensapice_drop_cz', 'fensapice_drop_vrh', 'fensapice_drop_vrh_1', 'fensapice_drop_vc', 'mixing_plane_thread', 'wsf', 'wsb', 'wsn', 'solar_fluxes', 'solar_shining_factor', 'radiating_s2s_surface', 'ac_options', 'impedance_0', 'impedance_1', 'impedance_2', 'ac_wave', 'les_spec']
    _child_classes = dict(
        phase=phase_17,
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        open_channel=open_channel,
        inlet_number=inlet_number,
        phase_spec=phase_spec,
        frame_of_reference=frame_of_reference,
        p0=p0,
        supersonic_or_initial_gauge_pressure=supersonic_or_initial_gauge_pressure,
        t0=t0,
        direction_spec=direction_spec,
        flow_spec=flow_spec,
        ht_local=ht_local,
        ht_total=ht_total,
        vmag=vmag,
        ht_bottom=ht_bottom,
        den_spec=den_spec,
        coordinate_system=coordinate_system,
        flow_direction_component=flow_direction_component,
        direction_vector_components=direction_vector_components,
        axis_direction_component=axis_direction_component_1,
        axis_origin_component=axis_origin_component_1,
        les_spec_name=les_spec_name,
        rfg_number_of_modes=rfg_number_of_modes,
        vm_number_of_vortices=vm_number_of_vortices,
        vm_streamwise_fluct=vm_streamwise_fluct,
        vm_mass_conservation=vm_mass_conservation,
        volumetric_synthetic_turbulence_generator=volumetric_synthetic_turbulence_generator,
        volumetric_synthetic_turbulence_generator_option=volumetric_synthetic_turbulence_generator_option,
        volumetric_synthetic_turbulence_generator_option_thickness=volumetric_synthetic_turbulence_generator_option_thickness,
        prevent_reverse_flow=prevent_reverse_flow,
        ke_spec=ke_spec,
        nut=nut,
        kl=kl,
        intermit=intermit,
        k=k,
        e=e,
        o=o,
        v2=v2,
        turb_intensity=turb_intensity,
        turb_length_scale=turb_length_scale,
        turb_hydraulic_diam=turb_hydraulic_diam,
        turb_viscosity_ratio=turb_viscosity_ratio,
        turb_viscosity_ratio_profile=turb_viscosity_ratio_profile,
        rst_spec=rst_spec,
        uu=uu,
        vv=vv,
        ww=ww,
        uv=uv,
        vw=vw,
        uw=uw,
        ksgs_spec=ksgs_spec,
        ksgs=ksgs,
        sgs_turb_intensity=sgs_turb_intensity,
        granular_temperature=granular_temperature,
        iac=iac,
        lsfun=lsfun,
        volume_fraction=volume_fraction,
        species_in_mole_fractions=species_in_mole_fractions,
        mf=mf,
        elec_potential_type=elec_potential_type,
        potential_value=potential_value,
        dual_potential_type=dual_potential_type,
        dual_potential_value=dual_potential_value,
        x_displacement_type=x_displacement_type,
        x_displacement_value=x_displacement_value,
        y_displacement_type=y_displacement_type,
        y_displacement_value=y_displacement_value,
        z_displacement_type=z_displacement_type,
        z_displacement_value=z_displacement_value,
        prob_mode_1=prob_mode_1,
        prob_mode_2=prob_mode_2,
        prob_mode_3=prob_mode_3,
        equ_required=equ_required,
        uds_bc=uds_bc,
        uds=uds,
        pb_disc_bc=pb_disc_bc,
        pb_disc=pb_disc,
        pb_qmom_bc=pb_qmom_bc,
        pb_qmom=pb_qmom,
        pb_smm_bc=pb_smm_bc,
        pb_smm=pb_smm,
        pb_dqmom_bc=pb_dqmom_bc,
        pb_dqmom=pb_dqmom,
        radiation_bc=radiation_bc,
        radial_direction_component=radial_direction_component,
        coll_dtheta=coll_dtheta,
        coll_dphi=coll_dphi,
        band_q_irrad=band_q_irrad,
        band_q_irrad_diffuse=band_q_irrad_diffuse,
        parallel_collimated_beam=parallel_collimated_beam,
        solar_direction=solar_direction,
        solar_irradiation=solar_irradiation,
        t_b_b_spec=t_b_b_spec,
        t_b_b=t_b_b,
        in_emiss=in_emiss,
        fmean=fmean,
        fvar=fvar,
        fmean2=fmean2,
        fvar2=fvar2,
        premixc=premixc,
        premixc_var=premixc_var,
        ecfm_sigma=ecfm_sigma,
        inert=inert,
        pollut_no=pollut_no,
        pollut_hcn=pollut_hcn,
        pollut_nh3=pollut_nh3,
        pollut_n2o=pollut_n2o,
        pollut_urea=pollut_urea,
        pollut_hnco=pollut_hnco,
        pollut_nco=pollut_nco,
        pollut_so2=pollut_so2,
        pollut_h2s=pollut_h2s,
        pollut_so3=pollut_so3,
        pollut_sh=pollut_sh,
        pollut_so=pollut_so,
        pollut_soot=pollut_soot,
        pollut_nuclei=pollut_nuclei,
        pollut_ctar=pollut_ctar,
        pollut_hg=pollut_hg,
        pollut_hgcl2=pollut_hgcl2,
        pollut_hcl=pollut_hcl,
        pollut_hgo=pollut_hgo,
        pollut_cl=pollut_cl,
        pollut_cl2=pollut_cl2,
        pollut_hgcl=pollut_hgcl,
        pollut_hocl=pollut_hocl,
        tss_scalar=tss_scalar,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        fensapice_flow_bc_subtype=fensapice_flow_bc_subtype,
        fensapice_drop_bccustom=fensapice_drop_bccustom,
        fensapice_drop_lwc=fensapice_drop_lwc,
        fensapice_drop_dtemp=fensapice_drop_dtemp,
        fensapice_drop_ddiam=fensapice_drop_ddiam,
        fensapice_drop_dv=fensapice_drop_dv,
        fensapice_drop_dx=fensapice_drop_dx,
        fensapice_drop_dy=fensapice_drop_dy,
        fensapice_drop_dz=fensapice_drop_dz,
        fensapice_dpm_surface_injection=fensapice_dpm_surface_injection,
        fensapice_dpm_inj_nstream=fensapice_dpm_inj_nstream,
        fensapice_drop_icc=fensapice_drop_icc,
        fensapice_drop_ctemp=fensapice_drop_ctemp,
        fensapice_drop_cdiam=fensapice_drop_cdiam,
        fensapice_drop_cv=fensapice_drop_cv,
        fensapice_drop_cx=fensapice_drop_cx,
        fensapice_drop_cy=fensapice_drop_cy,
        fensapice_drop_cz=fensapice_drop_cz,
        fensapice_drop_vrh=fensapice_drop_vrh,
        fensapice_drop_vrh_1=fensapice_drop_vrh_1,
        fensapice_drop_vc=fensapice_drop_vc,
        mixing_plane_thread=mixing_plane_thread,
        wsf=wsf,
        wsb=wsb,
        wsn=wsn,
        solar_fluxes=solar_fluxes,
        solar_shining_factor=solar_shining_factor,
        radiating_s2s_surface=radiating_s2s_surface,
        ac_options=ac_options,
        impedance_0=impedance_0,
        impedance_1=impedance_1,
        impedance_2=impedance_2,
        ac_wave=ac_wave,
        les_spec=les_spec,
    )
    return_type = 'object'

class pressure_inlet(NamedObject[pressure_inlet_child], CreatableNamedObjectMixinOld[pressure_inlet_child]):
    """
    'pressure_inlet' child.
    """
    _version = '222'
    fluent_name = 'pressure-inlet'
    _python_name = 'pressure_inlet'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = pressure_inlet_child
    return_type = 'object'

class phase_18_child(Group):
    """
    'child_object_type' of phase.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'phase_child'
    child_names = ['geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'open_channel', 'outlet_number', 'pressure_spec_method', 'press_spec', 'frame_of_reference', 'phase_spec', 'ht_local', 'p', 'p_profile_multiplier', 'ht_bottom', 'den_spec', 't0', 'direction_spec', 'coordinate_system', 'flow_direction_component', 'axis_direction_component', 'axis_origin_component', 'ke_spec', 'nut', 'kl', 'intermit', 'k', 'e', 'o', 'v2', 'turb_intensity', 'turb_length_scale', 'turb_hydraulic_diam', 'turb_viscosity_ratio', 'turb_viscosity_ratio_profile', 'rst_spec', 'uu', 'vv', 'ww', 'uv', 'vw', 'uw', 'ksgs_spec', 'ksgs', 'sgs_turb_intensity', 'radiation_bc', 'radial_direction_component', 'coll_dtheta', 'coll_dphi', 'band_q_irrad', 'band_q_irrad_diffuse', 'parallel_collimated_beam', 'solar_direction', 'solar_irradiation', 't_b_b_spec', 't_b_b', 'in_emiss', 'fmean', 'fmean2', 'fvar', 'fvar2', 'granular_temperature', 'iac', 'lsfun', 'vof_spec', 'volume_fraction', 'species_in_mole_fractions', 'mf', 'elec_potential_type', 'potential_value', 'dual_potential_type', 'dual_potential_value', 'x_displacement_type', 'x_displacement_value', 'y_displacement_type', 'y_displacement_value', 'z_displacement_type', 'z_displacement_value', 'prob_mode_1', 'prob_mode_2', 'prob_mode_3', 'premixc', 'premixc_var', 'ecfm_sigma', 'inert', 'pollut_no', 'pollut_hcn', 'pollut_nh3', 'pollut_n2o', 'pollut_urea', 'pollut_hnco', 'pollut_nco', 'pollut_so2', 'pollut_h2s', 'pollut_so3', 'pollut_sh', 'pollut_so', 'pollut_soot', 'pollut_nuclei', 'pollut_ctar', 'pollut_hg', 'pollut_hgcl2', 'pollut_hcl', 'pollut_hgo', 'pollut_cl', 'pollut_cl2', 'pollut_hgcl', 'pollut_hocl', 'tss_scalar', 'fensapice_flow_bc_subtype', 'uds_bc', 'uds', 'pb_disc_bc', 'pb_disc', 'pb_qmom_bc', 'pb_qmom', 'pb_smm_bc', 'pb_smm', 'pb_dqmom_bc', 'pb_dqmom', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'mixing_plane_thread', 'ac_options', 'p_backflow_spec', 'p_backflow_spec_gen', 'impedance_0', 'impedance_1', 'impedance_2', 'ac_wave', 'prevent_reverse_flow', 'radial', 'avg_press_spec', 'press_averaging_method', 'targeted_mf_boundary', 'targeted_mf', 'targeted_mf_pmax', 'targeted_mf_pmin', 'gen_nrbc_spec', 'wsf', 'wsb', 'wsn', 'solar_fluxes', 'solar_shining_factor', 'radiating_s2s_surface']
    _child_classes = dict(
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        open_channel=open_channel,
        outlet_number=outlet_number,
        pressure_spec_method=pressure_spec_method,
        press_spec=press_spec,
        frame_of_reference=frame_of_reference,
        phase_spec=phase_spec,
        ht_local=ht_local,
        p=p,
        p_profile_multiplier=p_profile_multiplier,
        ht_bottom=ht_bottom,
        den_spec=den_spec,
        t0=t0,
        direction_spec=direction_spec,
        coordinate_system=coordinate_system,
        flow_direction_component=flow_direction_component,
        axis_direction_component=axis_direction_component_1,
        axis_origin_component=axis_origin_component_1,
        ke_spec=ke_spec,
        nut=nut,
        kl=kl,
        intermit=intermit,
        k=k,
        e=e,
        o=o,
        v2=v2,
        turb_intensity=turb_intensity,
        turb_length_scale=turb_length_scale,
        turb_hydraulic_diam=turb_hydraulic_diam,
        turb_viscosity_ratio=turb_viscosity_ratio,
        turb_viscosity_ratio_profile=turb_viscosity_ratio_profile,
        rst_spec=rst_spec,
        uu=uu,
        vv=vv,
        ww=ww,
        uv=uv,
        vw=vw,
        uw=uw,
        ksgs_spec=ksgs_spec,
        ksgs=ksgs,
        sgs_turb_intensity=sgs_turb_intensity,
        radiation_bc=radiation_bc,
        radial_direction_component=radial_direction_component,
        coll_dtheta=coll_dtheta,
        coll_dphi=coll_dphi,
        band_q_irrad=band_q_irrad,
        band_q_irrad_diffuse=band_q_irrad_diffuse,
        parallel_collimated_beam=parallel_collimated_beam,
        solar_direction=solar_direction,
        solar_irradiation=solar_irradiation,
        t_b_b_spec=t_b_b_spec,
        t_b_b=t_b_b,
        in_emiss=in_emiss,
        fmean=fmean,
        fmean2=fmean2,
        fvar=fvar,
        fvar2=fvar2,
        granular_temperature=granular_temperature,
        iac=iac,
        lsfun=lsfun,
        vof_spec=vof_spec,
        volume_fraction=volume_fraction,
        species_in_mole_fractions=species_in_mole_fractions,
        mf=mf,
        elec_potential_type=elec_potential_type,
        potential_value=potential_value,
        dual_potential_type=dual_potential_type,
        dual_potential_value=dual_potential_value,
        x_displacement_type=x_displacement_type,
        x_displacement_value=x_displacement_value,
        y_displacement_type=y_displacement_type,
        y_displacement_value=y_displacement_value,
        z_displacement_type=z_displacement_type,
        z_displacement_value=z_displacement_value,
        prob_mode_1=prob_mode_1,
        prob_mode_2=prob_mode_2,
        prob_mode_3=prob_mode_3,
        premixc=premixc,
        premixc_var=premixc_var,
        ecfm_sigma=ecfm_sigma,
        inert=inert,
        pollut_no=pollut_no,
        pollut_hcn=pollut_hcn,
        pollut_nh3=pollut_nh3,
        pollut_n2o=pollut_n2o,
        pollut_urea=pollut_urea,
        pollut_hnco=pollut_hnco,
        pollut_nco=pollut_nco,
        pollut_so2=pollut_so2,
        pollut_h2s=pollut_h2s,
        pollut_so3=pollut_so3,
        pollut_sh=pollut_sh,
        pollut_so=pollut_so,
        pollut_soot=pollut_soot,
        pollut_nuclei=pollut_nuclei,
        pollut_ctar=pollut_ctar,
        pollut_hg=pollut_hg,
        pollut_hgcl2=pollut_hgcl2,
        pollut_hcl=pollut_hcl,
        pollut_hgo=pollut_hgo,
        pollut_cl=pollut_cl,
        pollut_cl2=pollut_cl2,
        pollut_hgcl=pollut_hgcl,
        pollut_hocl=pollut_hocl,
        tss_scalar=tss_scalar,
        fensapice_flow_bc_subtype=fensapice_flow_bc_subtype,
        uds_bc=uds_bc,
        uds=uds,
        pb_disc_bc=pb_disc_bc,
        pb_disc=pb_disc,
        pb_qmom_bc=pb_qmom_bc,
        pb_qmom=pb_qmom,
        pb_smm_bc=pb_smm_bc,
        pb_smm=pb_smm,
        pb_dqmom_bc=pb_dqmom_bc,
        pb_dqmom=pb_dqmom,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        mixing_plane_thread=mixing_plane_thread,
        ac_options=ac_options,
        p_backflow_spec=p_backflow_spec,
        p_backflow_spec_gen=p_backflow_spec_gen,
        impedance_0=impedance_0,
        impedance_1=impedance_1,
        impedance_2=impedance_2,
        ac_wave=ac_wave,
        prevent_reverse_flow=prevent_reverse_flow,
        radial=radial,
        avg_press_spec=avg_press_spec,
        press_averaging_method=press_averaging_method,
        targeted_mf_boundary=targeted_mf_boundary,
        targeted_mf=targeted_mf,
        targeted_mf_pmax=targeted_mf_pmax,
        targeted_mf_pmin=targeted_mf_pmin,
        gen_nrbc_spec=gen_nrbc_spec,
        wsf=wsf,
        wsb=wsb,
        wsn=wsn,
        solar_fluxes=solar_fluxes,
        solar_shining_factor=solar_shining_factor,
        radiating_s2s_surface=radiating_s2s_surface,
    )
    return_type = 'object'

class phase_18(NamedObject[phase_18_child], CreatableNamedObjectMixinOld[phase_18_child]):
    """
    'phase' child.
    """
    _version = '222'
    fluent_name = 'phase'
    _python_name = 'phase'
    child_object_type = phase_18_child
    return_type = 'object'

class pressure_outlet_child(Group):
    """
    'child_object_type' of pressure_outlet.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'pressure_outlet_child'
    child_names = ['phase', 'geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'open_channel', 'outlet_number', 'pressure_spec_method', 'press_spec', 'frame_of_reference', 'phase_spec', 'ht_local', 'p', 'p_profile_multiplier', 'ht_bottom', 'den_spec', 't0', 'direction_spec', 'coordinate_system', 'flow_direction_component', 'axis_direction_component', 'axis_origin_component', 'ke_spec', 'nut', 'kl', 'intermit', 'k', 'e', 'o', 'v2', 'turb_intensity', 'turb_length_scale', 'turb_hydraulic_diam', 'turb_viscosity_ratio', 'turb_viscosity_ratio_profile', 'rst_spec', 'uu', 'vv', 'ww', 'uv', 'vw', 'uw', 'ksgs_spec', 'ksgs', 'sgs_turb_intensity', 'radiation_bc', 'radial_direction_component', 'coll_dtheta', 'coll_dphi', 'band_q_irrad', 'band_q_irrad_diffuse', 'parallel_collimated_beam', 'solar_direction', 'solar_irradiation', 't_b_b_spec', 't_b_b', 'in_emiss', 'fmean', 'fmean2', 'fvar', 'fvar2', 'granular_temperature', 'iac', 'lsfun', 'vof_spec', 'volume_fraction', 'species_in_mole_fractions', 'mf', 'elec_potential_type', 'potential_value', 'dual_potential_type', 'dual_potential_value', 'x_displacement_type', 'x_displacement_value', 'y_displacement_type', 'y_displacement_value', 'z_displacement_type', 'z_displacement_value', 'prob_mode_1', 'prob_mode_2', 'prob_mode_3', 'premixc', 'premixc_var', 'ecfm_sigma', 'inert', 'pollut_no', 'pollut_hcn', 'pollut_nh3', 'pollut_n2o', 'pollut_urea', 'pollut_hnco', 'pollut_nco', 'pollut_so2', 'pollut_h2s', 'pollut_so3', 'pollut_sh', 'pollut_so', 'pollut_soot', 'pollut_nuclei', 'pollut_ctar', 'pollut_hg', 'pollut_hgcl2', 'pollut_hcl', 'pollut_hgo', 'pollut_cl', 'pollut_cl2', 'pollut_hgcl', 'pollut_hocl', 'tss_scalar', 'fensapice_flow_bc_subtype', 'uds_bc', 'uds', 'pb_disc_bc', 'pb_disc', 'pb_qmom_bc', 'pb_qmom', 'pb_smm_bc', 'pb_smm', 'pb_dqmom_bc', 'pb_dqmom', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'mixing_plane_thread', 'ac_options', 'p_backflow_spec', 'p_backflow_spec_gen', 'impedance_0', 'impedance_1', 'impedance_2', 'ac_wave', 'prevent_reverse_flow', 'radial', 'avg_press_spec', 'press_averaging_method', 'targeted_mf_boundary', 'targeted_mf', 'targeted_mf_pmax', 'targeted_mf_pmin', 'gen_nrbc_spec', 'wsf', 'wsb', 'wsn', 'solar_fluxes', 'solar_shining_factor', 'radiating_s2s_surface']
    _child_classes = dict(
        phase=phase_18,
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        open_channel=open_channel,
        outlet_number=outlet_number,
        pressure_spec_method=pressure_spec_method,
        press_spec=press_spec,
        frame_of_reference=frame_of_reference,
        phase_spec=phase_spec,
        ht_local=ht_local,
        p=p,
        p_profile_multiplier=p_profile_multiplier,
        ht_bottom=ht_bottom,
        den_spec=den_spec,
        t0=t0,
        direction_spec=direction_spec,
        coordinate_system=coordinate_system,
        flow_direction_component=flow_direction_component,
        axis_direction_component=axis_direction_component_1,
        axis_origin_component=axis_origin_component_1,
        ke_spec=ke_spec,
        nut=nut,
        kl=kl,
        intermit=intermit,
        k=k,
        e=e,
        o=o,
        v2=v2,
        turb_intensity=turb_intensity,
        turb_length_scale=turb_length_scale,
        turb_hydraulic_diam=turb_hydraulic_diam,
        turb_viscosity_ratio=turb_viscosity_ratio,
        turb_viscosity_ratio_profile=turb_viscosity_ratio_profile,
        rst_spec=rst_spec,
        uu=uu,
        vv=vv,
        ww=ww,
        uv=uv,
        vw=vw,
        uw=uw,
        ksgs_spec=ksgs_spec,
        ksgs=ksgs,
        sgs_turb_intensity=sgs_turb_intensity,
        radiation_bc=radiation_bc,
        radial_direction_component=radial_direction_component,
        coll_dtheta=coll_dtheta,
        coll_dphi=coll_dphi,
        band_q_irrad=band_q_irrad,
        band_q_irrad_diffuse=band_q_irrad_diffuse,
        parallel_collimated_beam=parallel_collimated_beam,
        solar_direction=solar_direction,
        solar_irradiation=solar_irradiation,
        t_b_b_spec=t_b_b_spec,
        t_b_b=t_b_b,
        in_emiss=in_emiss,
        fmean=fmean,
        fmean2=fmean2,
        fvar=fvar,
        fvar2=fvar2,
        granular_temperature=granular_temperature,
        iac=iac,
        lsfun=lsfun,
        vof_spec=vof_spec,
        volume_fraction=volume_fraction,
        species_in_mole_fractions=species_in_mole_fractions,
        mf=mf,
        elec_potential_type=elec_potential_type,
        potential_value=potential_value,
        dual_potential_type=dual_potential_type,
        dual_potential_value=dual_potential_value,
        x_displacement_type=x_displacement_type,
        x_displacement_value=x_displacement_value,
        y_displacement_type=y_displacement_type,
        y_displacement_value=y_displacement_value,
        z_displacement_type=z_displacement_type,
        z_displacement_value=z_displacement_value,
        prob_mode_1=prob_mode_1,
        prob_mode_2=prob_mode_2,
        prob_mode_3=prob_mode_3,
        premixc=premixc,
        premixc_var=premixc_var,
        ecfm_sigma=ecfm_sigma,
        inert=inert,
        pollut_no=pollut_no,
        pollut_hcn=pollut_hcn,
        pollut_nh3=pollut_nh3,
        pollut_n2o=pollut_n2o,
        pollut_urea=pollut_urea,
        pollut_hnco=pollut_hnco,
        pollut_nco=pollut_nco,
        pollut_so2=pollut_so2,
        pollut_h2s=pollut_h2s,
        pollut_so3=pollut_so3,
        pollut_sh=pollut_sh,
        pollut_so=pollut_so,
        pollut_soot=pollut_soot,
        pollut_nuclei=pollut_nuclei,
        pollut_ctar=pollut_ctar,
        pollut_hg=pollut_hg,
        pollut_hgcl2=pollut_hgcl2,
        pollut_hcl=pollut_hcl,
        pollut_hgo=pollut_hgo,
        pollut_cl=pollut_cl,
        pollut_cl2=pollut_cl2,
        pollut_hgcl=pollut_hgcl,
        pollut_hocl=pollut_hocl,
        tss_scalar=tss_scalar,
        fensapice_flow_bc_subtype=fensapice_flow_bc_subtype,
        uds_bc=uds_bc,
        uds=uds,
        pb_disc_bc=pb_disc_bc,
        pb_disc=pb_disc,
        pb_qmom_bc=pb_qmom_bc,
        pb_qmom=pb_qmom,
        pb_smm_bc=pb_smm_bc,
        pb_smm=pb_smm,
        pb_dqmom_bc=pb_dqmom_bc,
        pb_dqmom=pb_dqmom,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        mixing_plane_thread=mixing_plane_thread,
        ac_options=ac_options,
        p_backflow_spec=p_backflow_spec,
        p_backflow_spec_gen=p_backflow_spec_gen,
        impedance_0=impedance_0,
        impedance_1=impedance_1,
        impedance_2=impedance_2,
        ac_wave=ac_wave,
        prevent_reverse_flow=prevent_reverse_flow,
        radial=radial,
        avg_press_spec=avg_press_spec,
        press_averaging_method=press_averaging_method,
        targeted_mf_boundary=targeted_mf_boundary,
        targeted_mf=targeted_mf,
        targeted_mf_pmax=targeted_mf_pmax,
        targeted_mf_pmin=targeted_mf_pmin,
        gen_nrbc_spec=gen_nrbc_spec,
        wsf=wsf,
        wsb=wsb,
        wsn=wsn,
        solar_fluxes=solar_fluxes,
        solar_shining_factor=solar_shining_factor,
        radiating_s2s_surface=radiating_s2s_surface,
    )
    return_type = 'object'

class pressure_outlet(NamedObject[pressure_outlet_child], CreatableNamedObjectMixinOld[pressure_outlet_child]):
    """
    'pressure_outlet' child.
    """
    _version = '222'
    fluent_name = 'pressure-outlet'
    _python_name = 'pressure_outlet'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = pressure_outlet_child
    return_type = 'object'

class kc(Group):
    """
    'kc' child.
    """
    _version = '222'
    fluent_name = 'kc'
    _python_name = 'kc'
    child_names = ['method', 'number_of_coeff', 'function_of', 'coefficients', 'constant', 'piecewise_polynomial', 'piecewise_linear']
    _child_classes = dict(
        method=method,
        number_of_coeff=number_of_coeff,
        function_of=function_of,
        coefficients=coefficients,
        constant=constant,
        piecewise_polynomial=piecewise_polynomial,
        piecewise_linear=piecewise_linear,
    )
    return_type = 'object'

class hc(Group):
    """
    'hc' child.
    """
    _version = '222'
    fluent_name = 'hc'
    _python_name = 'hc'
    child_names = ['method', 'number_of_coeff', 'function_of', 'coefficients', 'constant', 'piecewise_polynomial', 'piecewise_linear']
    _child_classes = dict(
        method=method,
        number_of_coeff=number_of_coeff,
        function_of=function_of,
        coefficients=coefficients,
        constant=constant,
        piecewise_polynomial=piecewise_polynomial,
        piecewise_linear=piecewise_linear,
    )
    return_type = 'object'

class t_1(Real, AllowedValuesMixin):
    """
    't' child.
    """
    _version = '222'
    fluent_name = 't'
    _python_name = 't'
    return_type = 'object'

class q_1(Real, AllowedValuesMixin):
    """
    'q' child.
    """
    _version = '222'
    fluent_name = 'q'
    _python_name = 'q'
    return_type = 'object'

class phase_19_child(Group):
    """
    'child_object_type' of phase.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'phase_child'
    child_names = ['geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'porous_jump_turb_wall_treatment', 'kc', 'hc', 't', 'q', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'strength']
    _child_classes = dict(
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        porous_jump_turb_wall_treatment=porous_jump_turb_wall_treatment,
        kc=kc,
        hc=hc,
        t=t_1,
        q=q_1,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        strength=strength,
    )
    return_type = 'object'

class phase_19(NamedObject[phase_19_child], CreatableNamedObjectMixinOld[phase_19_child]):
    """
    'phase' child.
    """
    _version = '222'
    fluent_name = 'phase'
    _python_name = 'phase'
    child_object_type = phase_19_child
    return_type = 'object'

class radiator_child(Group):
    """
    'child_object_type' of radiator.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'radiator_child'
    child_names = ['phase', 'geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'porous_jump_turb_wall_treatment', 'kc', 'hc', 't', 'q', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'strength']
    _child_classes = dict(
        phase=phase_19,
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        porous_jump_turb_wall_treatment=porous_jump_turb_wall_treatment,
        kc=kc,
        hc=hc,
        t=t_1,
        q=q_1,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        strength=strength,
    )
    return_type = 'object'

class radiator(NamedObject[radiator_child], CreatableNamedObjectMixinOld[radiator_child]):
    """
    'radiator' child.
    """
    _version = '222'
    fluent_name = 'radiator'
    _python_name = 'radiator'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = radiator_child
    return_type = 'object'

class vm_nvortices(Integer, AllowedValuesMixin):
    """
    'vm_nvortices' child.
    """
    _version = '222'
    fluent_name = 'vm-nvortices'
    _python_name = 'vm_nvortices'
    return_type = 'object'

class les_embedded_fluctuations(String, AllowedValuesMixin):
    """
    'les_embedded_fluctuations' child.
    """
    _version = '222'
    fluent_name = 'les-embedded-fluctuations'
    _python_name = 'les_embedded_fluctuations'
    return_type = 'object'

class phase_20_child(Group):
    """
    'child_object_type' of phase.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'phase_child'
    child_names = ['geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'les_spec_name', 'rfg_number_of_modes', 'vm_nvortices', 'les_embedded_fluctuations']
    _child_classes = dict(
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        les_spec_name=les_spec_name,
        rfg_number_of_modes=rfg_number_of_modes,
        vm_nvortices=vm_nvortices,
        les_embedded_fluctuations=les_embedded_fluctuations,
    )
    return_type = 'object'

class phase_20(NamedObject[phase_20_child], CreatableNamedObjectMixinOld[phase_20_child]):
    """
    'phase' child.
    """
    _version = '222'
    fluent_name = 'phase'
    _python_name = 'phase'
    child_object_type = phase_20_child
    return_type = 'object'

class rans_les_interface_child(Group):
    """
    'child_object_type' of rans_les_interface.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'rans_les_interface_child'
    child_names = ['phase', 'geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'les_spec_name', 'rfg_number_of_modes', 'vm_nvortices', 'les_embedded_fluctuations']
    _child_classes = dict(
        phase=phase_20,
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        les_spec_name=les_spec_name,
        rfg_number_of_modes=rfg_number_of_modes,
        vm_nvortices=vm_nvortices,
        les_embedded_fluctuations=les_embedded_fluctuations,
    )
    return_type = 'object'

class rans_les_interface(NamedObject[rans_les_interface_child], CreatableNamedObjectMixinOld[rans_les_interface_child]):
    """
    'rans_les_interface' child.
    """
    _version = '222'
    fluent_name = 'rans-les-interface'
    _python_name = 'rans_les_interface'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = rans_les_interface_child
    return_type = 'object'

class pid(Group):
    """
    'pid' child.
    """
    _version = '222'
    fluent_name = 'pid'
    _python_name = 'pid'
    child_names = ['method', 'number_of_coeff', 'function_of', 'coefficients', 'constant', 'piecewise_polynomial', 'piecewise_linear']
    _child_classes = dict(
        method=method,
        number_of_coeff=number_of_coeff,
        function_of=function_of,
        coefficients=coefficients,
        constant=constant,
        piecewise_polynomial=piecewise_polynomial,
        piecewise_linear=piecewise_linear,
    )
    return_type = 'object'

class temperature_spec(String, AllowedValuesMixin):
    """
    'temperature_spec' child.
    """
    _version = '222'
    fluent_name = 'temperature-spec'
    _python_name = 'temperature_spec'
    return_type = 'object'

class temperature_rise(Group):
    """
    'temperature_rise' child.
    """
    _version = '222'
    fluent_name = 'temperature-rise'
    _python_name = 'temperature_rise'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class heat_source(Group):
    """
    'heat_source' child.
    """
    _version = '222'
    fluent_name = 'heat-source'
    _python_name = 'heat_source'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class tinf(Real, AllowedValuesMixin):
    """
    'tinf' child.
    """
    _version = '222'
    fluent_name = 'tinf'
    _python_name = 'tinf'
    return_type = 'object'

class mass_flow_multiplier_child(Group):
    """
    'child_object_type' of mass_flow_multiplier.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'mass_flow_multiplier_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class mass_flow_multiplier(NamedObject[mass_flow_multiplier_child], CreatableNamedObjectMixinOld[mass_flow_multiplier_child]):
    """
    'mass_flow_multiplier' child.
    """
    _version = '222'
    fluent_name = 'mass-flow-multiplier'
    _python_name = 'mass_flow_multiplier'
    child_object_type = mass_flow_multiplier_child
    return_type = 'object'

class phase_21_child(Group):
    """
    'child_object_type' of phase.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'phase_child'
    child_names = ['geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'pid', 'temperature_spec', 'temperature_rise', 'heat_source', 'tinf', 'hc', 'direction_spec', 'coordinate_system', 'flow_direction_component', 'direction_vector_components', 'ke_spec', 'nut', 'kl', 'intermit', 'k', 'e', 'o', 'v2', 'turb_intensity', 'turb_length_scale', 'turb_hydraulic_diam', 'turb_viscosity_ratio', 'turb_viscosity_ratio_profile', 'rst_spec', 'uu', 'vv', 'ww', 'uv', 'vw', 'uw', 'ksgs_spec', 'ksgs', 'sgs_turb_intensity', 'mass_flow_multiplier', 'solar_fluxes', 'solar_shining_factor']
    _child_classes = dict(
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        pid=pid,
        temperature_spec=temperature_spec,
        temperature_rise=temperature_rise,
        heat_source=heat_source,
        tinf=tinf,
        hc=hc,
        direction_spec=direction_spec,
        coordinate_system=coordinate_system,
        flow_direction_component=flow_direction_component,
        direction_vector_components=direction_vector_components,
        ke_spec=ke_spec,
        nut=nut,
        kl=kl,
        intermit=intermit,
        k=k,
        e=e,
        o=o,
        v2=v2,
        turb_intensity=turb_intensity,
        turb_length_scale=turb_length_scale,
        turb_hydraulic_diam=turb_hydraulic_diam,
        turb_viscosity_ratio=turb_viscosity_ratio,
        turb_viscosity_ratio_profile=turb_viscosity_ratio_profile,
        rst_spec=rst_spec,
        uu=uu,
        vv=vv,
        ww=ww,
        uv=uv,
        vw=vw,
        uw=uw,
        ksgs_spec=ksgs_spec,
        ksgs=ksgs,
        sgs_turb_intensity=sgs_turb_intensity,
        mass_flow_multiplier=mass_flow_multiplier,
        solar_fluxes=solar_fluxes,
        solar_shining_factor=solar_shining_factor,
    )
    return_type = 'object'

class phase_21(NamedObject[phase_21_child], CreatableNamedObjectMixinOld[phase_21_child]):
    """
    'phase' child.
    """
    _version = '222'
    fluent_name = 'phase'
    _python_name = 'phase'
    child_object_type = phase_21_child
    return_type = 'object'

class recirculation_inlet_child(Group):
    """
    'child_object_type' of recirculation_inlet.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'recirculation_inlet_child'
    child_names = ['phase', 'geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'pid', 'temperature_spec', 'temperature_rise', 'heat_source', 'tinf', 'hc', 'direction_spec', 'coordinate_system', 'flow_direction_component', 'direction_vector_components', 'ke_spec', 'nut', 'kl', 'intermit', 'k', 'e', 'o', 'v2', 'turb_intensity', 'turb_length_scale', 'turb_hydraulic_diam', 'turb_viscosity_ratio', 'turb_viscosity_ratio_profile', 'rst_spec', 'uu', 'vv', 'ww', 'uv', 'vw', 'uw', 'ksgs_spec', 'ksgs', 'sgs_turb_intensity', 'mass_flow_multiplier', 'solar_fluxes', 'solar_shining_factor']
    _child_classes = dict(
        phase=phase_21,
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        pid=pid,
        temperature_spec=temperature_spec,
        temperature_rise=temperature_rise,
        heat_source=heat_source,
        tinf=tinf,
        hc=hc,
        direction_spec=direction_spec,
        coordinate_system=coordinate_system,
        flow_direction_component=flow_direction_component,
        direction_vector_components=direction_vector_components,
        ke_spec=ke_spec,
        nut=nut,
        kl=kl,
        intermit=intermit,
        k=k,
        e=e,
        o=o,
        v2=v2,
        turb_intensity=turb_intensity,
        turb_length_scale=turb_length_scale,
        turb_hydraulic_diam=turb_hydraulic_diam,
        turb_viscosity_ratio=turb_viscosity_ratio,
        turb_viscosity_ratio_profile=turb_viscosity_ratio_profile,
        rst_spec=rst_spec,
        uu=uu,
        vv=vv,
        ww=ww,
        uv=uv,
        vw=vw,
        uw=uw,
        ksgs_spec=ksgs_spec,
        ksgs=ksgs,
        sgs_turb_intensity=sgs_turb_intensity,
        mass_flow_multiplier=mass_flow_multiplier,
        solar_fluxes=solar_fluxes,
        solar_shining_factor=solar_shining_factor,
    )
    return_type = 'object'

class recirculation_inlet(NamedObject[recirculation_inlet_child], CreatableNamedObjectMixinOld[recirculation_inlet_child]):
    """
    'recirculation_inlet' child.
    """
    _version = '222'
    fluent_name = 'recirculation-inlet'
    _python_name = 'recirculation_inlet'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = recirculation_inlet_child
    return_type = 'object'

class phase_22_child(Group):
    """
    'child_object_type' of phase.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'phase_child'
    child_names = ['geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'flow_spec', 'mass_flow', 'mass_flux', 'solar_fluxes', 'solar_shining_factor']
    _child_classes = dict(
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        flow_spec=flow_spec,
        mass_flow=mass_flow,
        mass_flux=mass_flux,
        solar_fluxes=solar_fluxes,
        solar_shining_factor=solar_shining_factor,
    )
    return_type = 'object'

class phase_22(NamedObject[phase_22_child], CreatableNamedObjectMixinOld[phase_22_child]):
    """
    'phase' child.
    """
    _version = '222'
    fluent_name = 'phase'
    _python_name = 'phase'
    child_object_type = phase_22_child
    return_type = 'object'

class recirculation_outlet_child(Group):
    """
    'child_object_type' of recirculation_outlet.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'recirculation_outlet_child'
    child_names = ['phase', 'geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'flow_spec', 'mass_flow', 'mass_flux', 'solar_fluxes', 'solar_shining_factor']
    _child_classes = dict(
        phase=phase_22,
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        flow_spec=flow_spec,
        mass_flow=mass_flow,
        mass_flux=mass_flux,
        solar_fluxes=solar_fluxes,
        solar_shining_factor=solar_shining_factor,
    )
    return_type = 'object'

class recirculation_outlet(NamedObject[recirculation_outlet_child], CreatableNamedObjectMixinOld[recirculation_outlet_child]):
    """
    'recirculation_outlet' child.
    """
    _version = '222'
    fluent_name = 'recirculation-outlet'
    _python_name = 'recirculation_outlet'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = recirculation_outlet_child
    return_type = 'object'

class shadow_child(Group):
    """
    'child_object_type' of shadow.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'shadow_child'
    child_names = ['phase', 'geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread']
    _child_classes = dict(
        phase=phase_2,
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
    )
    return_type = 'object'

class shadow(NamedObject[shadow_child], CreatableNamedObjectMixinOld[shadow_child]):
    """
    'shadow' child.
    """
    _version = '222'
    fluent_name = 'shadow'
    _python_name = 'shadow'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = shadow_child
    return_type = 'object'

class symmetry_child(Group):
    """
    'child_object_type' of symmetry.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'symmetry_child'
    child_names = ['phase', 'geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread']
    _child_classes = dict(
        phase=phase_2,
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
    )
    return_type = 'object'

class symmetry(NamedObject[symmetry_child], CreatableNamedObjectMixinOld[symmetry_child]):
    """
    'symmetry' child.
    """
    _version = '222'
    fluent_name = 'symmetry'
    _python_name = 'symmetry'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = symmetry_child
    return_type = 'object'

class open_channel_wave_bc(Boolean, AllowedValuesMixin):
    """
    'open_channel_wave_bc' child.
    """
    _version = '222'
    fluent_name = 'open-channel-wave-bc?'
    _python_name = 'open_channel_wave_bc'
    return_type = 'object'

class ocw_vel_segregated(Boolean, AllowedValuesMixin):
    """
    'ocw_vel_segregated' child.
    """
    _version = '222'
    fluent_name = 'ocw-vel-segregated?'
    _python_name = 'ocw_vel_segregated'
    return_type = 'object'

class velocity_spec(String, AllowedValuesMixin):
    """
    'velocity_spec' child.
    """
    _version = '222'
    fluent_name = 'velocity-spec'
    _python_name = 'velocity_spec'
    return_type = 'object'

class wave_velocity_spec(String, AllowedValuesMixin):
    """
    'wave_velocity_spec' child.
    """
    _version = '222'
    fluent_name = 'wave-velocity-spec'
    _python_name = 'wave_velocity_spec'
    return_type = 'object'

class avg_flow_velocity(Group):
    """
    'avg_flow_velocity' child.
    """
    _version = '222'
    fluent_name = 'avg-flow-velocity'
    _python_name = 'avg_flow_velocity'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class ocw_ship_vel_spec(String, AllowedValuesMixin):
    """
    'ocw_ship_vel_spec' child.
    """
    _version = '222'
    fluent_name = 'ocw-ship-vel-spec'
    _python_name = 'ocw_ship_vel_spec'
    return_type = 'object'

class ocw_ship_vmag(Group):
    """
    'ocw_ship_vmag' child.
    """
    _version = '222'
    fluent_name = 'ocw-ship-vmag'
    _python_name = 'ocw_ship_vmag'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class moving_object_direction_components_child(Group):
    """
    'child_object_type' of moving_object_direction_components.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'moving_object_direction_components_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class moving_object_direction_components(ListObject[moving_object_direction_components_child]):
    """
    'moving_object_direction_components' child.
    """
    _version = '222'
    fluent_name = 'moving-object-direction-components'
    _python_name = 'moving_object_direction_components'
    child_object_type = moving_object_direction_components_child
    return_type = 'object'

class ocw_sp_vel_spec(String, AllowedValuesMixin):
    """
    'ocw_sp_vel_spec' child.
    """
    _version = '222'
    fluent_name = 'ocw-sp-vel-spec'
    _python_name = 'ocw_sp_vel_spec'
    return_type = 'object'

class ocw_sp_vmag(Group):
    """
    'ocw_sp_vmag' child.
    """
    _version = '222'
    fluent_name = 'ocw-sp-vmag'
    _python_name = 'ocw_sp_vmag'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class secondary_phase_direction_components_child(Group):
    """
    'child_object_type' of secondary_phase_direction_components.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'secondary_phase_direction_components_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class secondary_phase_direction_components(ListObject[secondary_phase_direction_components_child]):
    """
    'secondary_phase_direction_components' child.
    """
    _version = '222'
    fluent_name = 'secondary-phase-direction-components'
    _python_name = 'secondary_phase_direction_components'
    child_object_type = secondary_phase_direction_components_child
    return_type = 'object'

class ocw_pp_vel_spec(String, AllowedValuesMixin):
    """
    'ocw_pp_vel_spec' child.
    """
    _version = '222'
    fluent_name = 'ocw-pp-vel-spec'
    _python_name = 'ocw_pp_vel_spec'
    return_type = 'object'

class ocw_pp_ref_ht(Real, AllowedValuesMixin):
    """
    'ocw_pp_ref_ht' child.
    """
    _version = '222'
    fluent_name = 'ocw-pp-ref-ht'
    _python_name = 'ocw_pp_ref_ht'
    return_type = 'object'

class ocw_pp_power_coeff(Real, AllowedValuesMixin):
    """
    'ocw_pp_power_coeff' child.
    """
    _version = '222'
    fluent_name = 'ocw-pp-power-coeff'
    _python_name = 'ocw_pp_power_coeff'
    return_type = 'object'

class ocw_pp_vmag(Group):
    """
    'ocw_pp_vmag' child.
    """
    _version = '222'
    fluent_name = 'ocw-pp-vmag'
    _python_name = 'ocw_pp_vmag'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class ocw_pp_vmag_ref(Group):
    """
    'ocw_pp_vmag_ref' child.
    """
    _version = '222'
    fluent_name = 'ocw-pp-vmag-ref'
    _python_name = 'ocw_pp_vmag_ref'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class primary_phase_direction_components_child(Group):
    """
    'child_object_type' of primary_phase_direction_components.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'primary_phase_direction_components_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class primary_phase_direction_components(ListObject[primary_phase_direction_components_child]):
    """
    'primary_phase_direction_components' child.
    """
    _version = '222'
    fluent_name = 'primary-phase-direction-components'
    _python_name = 'primary_phase_direction_components'
    child_object_type = primary_phase_direction_components_child
    return_type = 'object'

class p_sup(Group):
    """
    'p_sup' child.
    """
    _version = '222'
    fluent_name = 'p-sup'
    _python_name = 'p_sup'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class velocity_component_child(Group):
    """
    'child_object_type' of velocity_component.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'velocity_component_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class velocity_component(ListObject[velocity_component_child]):
    """
    'velocity_component' child.
    """
    _version = '222'
    fluent_name = 'velocity-component'
    _python_name = 'velocity_component'
    child_object_type = velocity_component_child
    return_type = 'object'

class omega_swirl(Real, AllowedValuesMixin):
    """
    'omega_swirl' child.
    """
    _version = '222'
    fluent_name = 'omega-swirl'
    _python_name = 'omega_swirl'
    return_type = 'object'

class wave_bc_type(String, AllowedValuesMixin):
    """
    'wave_bc_type' child.
    """
    _version = '222'
    fluent_name = 'wave-bc-type'
    _python_name = 'wave_bc_type'
    return_type = 'object'

class wave_dir_spec(String, AllowedValuesMixin):
    """
    'wave_dir_spec' child.
    """
    _version = '222'
    fluent_name = 'wave-dir-spec'
    _python_name = 'wave_dir_spec'
    return_type = 'object'

class wave_modeling_type(String, AllowedValuesMixin):
    """
    'wave_modeling_type' child.
    """
    _version = '222'
    fluent_name = 'wave-modeling-type'
    _python_name = 'wave_modeling_type'
    return_type = 'object'

class theory(String, AllowedValuesMixin):
    """
    'theory' child.
    """
    _version = '222'
    fluent_name = 'theory'
    _python_name = 'theory'
    return_type = 'object'

class wave_ht(Group):
    """
    'wave_ht' child.
    """
    _version = '222'
    fluent_name = 'wave-ht'
    _python_name = 'wave_ht'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class wave_len(Group):
    """
    'wave_len' child.
    """
    _version = '222'
    fluent_name = 'wave-len'
    _python_name = 'wave_len'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class phase_diff(Group):
    """
    'phase_diff' child.
    """
    _version = '222'
    fluent_name = 'phase-diff'
    _python_name = 'phase_diff'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class heading_angle(Group):
    """
    'heading_angle' child.
    """
    _version = '222'
    fluent_name = 'heading-angle'
    _python_name = 'heading_angle'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class wave_list_child(Group):
    """
    'child_object_type' of wave_list.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'wave_list_child'
    child_names = ['theory', 'wave_ht', 'wave_len', 'phase_diff', 'heading_angle']
    _child_classes = dict(
        theory=theory,
        wave_ht=wave_ht,
        wave_len=wave_len,
        phase_diff=phase_diff,
        heading_angle=heading_angle,
    )
    return_type = 'object'

class wave_list(ListObject[wave_list_child]):
    """
    'wave_list' child.
    """
    _version = '222'
    fluent_name = 'wave-list'
    _python_name = 'wave_list'
    child_object_type = wave_list_child
    return_type = 'object'

class offset(Group):
    """
    'offset' child.
    """
    _version = '222'
    fluent_name = 'offset'
    _python_name = 'offset'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class wave_list_shallow_child(Group):
    """
    'child_object_type' of wave_list_shallow.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'wave_list_shallow_child'
    child_names = ['theory', 'wave_ht', 'wave_len', 'offset', 'heading_angle']
    _child_classes = dict(
        theory=theory,
        wave_ht=wave_ht,
        wave_len=wave_len,
        offset=offset,
        heading_angle=heading_angle,
    )
    return_type = 'object'

class wave_list_shallow(ListObject[wave_list_shallow_child]):
    """
    'wave_list_shallow' child.
    """
    _version = '222'
    fluent_name = 'wave-list-shallow'
    _python_name = 'wave_list_shallow'
    child_object_type = wave_list_shallow_child
    return_type = 'object'

class wave_spect_method_freq(String, AllowedValuesMixin):
    """
    'wave_spect_method_freq' child.
    """
    _version = '222'
    fluent_name = 'wave-spect-method-freq'
    _python_name = 'wave_spect_method_freq'
    return_type = 'object'

class wave_spect_factor(Real, AllowedValuesMixin):
    """
    'wave_spect_factor' child.
    """
    _version = '222'
    fluent_name = 'wave-spect-factor'
    _python_name = 'wave_spect_factor'
    return_type = 'object'

class wave_spect_sig_wave_ht(Group):
    """
    'wave_spect_sig_wave_ht' child.
    """
    _version = '222'
    fluent_name = 'wave-spect-sig-wave-ht'
    _python_name = 'wave_spect_sig_wave_ht'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class wave_spect_peak_freq(Group):
    """
    'wave_spect_peak_freq' child.
    """
    _version = '222'
    fluent_name = 'wave-spect-peak-freq'
    _python_name = 'wave_spect_peak_freq'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class wave_spect_min_freq(Group):
    """
    'wave_spect_min_freq' child.
    """
    _version = '222'
    fluent_name = 'wave-spect-min-freq'
    _python_name = 'wave_spect_min_freq'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class wave_spect_max_freq(Group):
    """
    'wave_spect_max_freq' child.
    """
    _version = '222'
    fluent_name = 'wave-spect-max-freq'
    _python_name = 'wave_spect_max_freq'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class wave_spect_freq_components(Integer, AllowedValuesMixin):
    """
    'wave_spect_freq_components' child.
    """
    _version = '222'
    fluent_name = 'wave-spect-freq-components'
    _python_name = 'wave_spect_freq_components'
    return_type = 'object'

class wave_spect_method_dir(String, AllowedValuesMixin):
    """
    'wave_spect_method_dir' child.
    """
    _version = '222'
    fluent_name = 'wave-spect-method-dir'
    _python_name = 'wave_spect_method_dir'
    return_type = 'object'

class wave_spect_s(Integer, AllowedValuesMixin):
    """
    'wave_spect_s' child.
    """
    _version = '222'
    fluent_name = 'wave-spect-s'
    _python_name = 'wave_spect_s'
    return_type = 'object'

class wave_spect_mean_angle(Group):
    """
    'wave_spect_mean_angle' child.
    """
    _version = '222'
    fluent_name = 'wave-spect-mean-angle'
    _python_name = 'wave_spect_mean_angle'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class wave_spect_deviation(Group):
    """
    'wave_spect_deviation' child.
    """
    _version = '222'
    fluent_name = 'wave-spect-deviation'
    _python_name = 'wave_spect_deviation'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class wave_spect_dir_components(Integer, AllowedValuesMixin):
    """
    'wave_spect_dir_components' child.
    """
    _version = '222'
    fluent_name = 'wave-spect-dir-components'
    _python_name = 'wave_spect_dir_components'
    return_type = 'object'

class mean_and_std_deviation(RealList):
    """
    Mean and standard deviation.
    """
    _version = '222'
    fluent_name = 'mean-and-std-deviation'
    _python_name = 'mean_and_std_deviation'
    return_type = 'object'

class pb_disc_components_child(Group):
    """
    'child_object_type' of pb_disc_components.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'pb_disc_components_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class pb_disc_components(ListObject[pb_disc_components_child]):
    """
    'pb_disc_components' child.
    """
    _version = '222'
    fluent_name = 'pb-disc-components'
    _python_name = 'pb_disc_components'
    child_object_type = pb_disc_components_child
    return_type = 'object'

class pb_disc_1(Group):
    """
    'pb_disc' child.
    """
    _version = '222'
    fluent_name = 'pb-disc'
    _python_name = 'pb_disc'
    child_names = ['mean_and_std_deviation', 'pb_disc_components']
    _child_classes = dict(
        mean_and_std_deviation=mean_and_std_deviation,
        pb_disc_components=pb_disc_components,
    )
    return_type = 'object'

class phase_23_child(Group):
    """
    'child_object_type' of phase.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'phase_child'
    child_names = ['geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'open_channel_wave_bc', 'ocw_vel_segregated', 'velocity_spec', 'frame_of_reference', 'vmag', 'wave_velocity_spec', 'avg_flow_velocity', 'ocw_ship_vel_spec', 'ocw_ship_vmag', 'moving_object_direction_components', 'ocw_sp_vel_spec', 'ocw_sp_vmag', 'secondary_phase_direction_components', 'ocw_pp_vel_spec', 'ocw_pp_ref_ht', 'ocw_pp_power_coeff', 'ocw_pp_vmag', 'ocw_pp_vmag_ref', 'primary_phase_direction_components', 'p_sup', 'coordinate_system', 'velocity_component', 'flow_direction_component', 'axis_direction_component', 'axis_origin_component', 'omega_swirl', 'phase_spec', 'wave_bc_type', 'ht_local', 'ht_bottom', 'wave_dir_spec', 'wave_modeling_type', 'wave_list', 'wave_list_shallow', 'wave_spect_method_freq', 'wave_spect_factor', 'wave_spect_sig_wave_ht', 'wave_spect_peak_freq', 'wave_spect_min_freq', 'wave_spect_max_freq', 'wave_spect_freq_components', 'wave_spect_method_dir', 'wave_spect_s', 'wave_spect_mean_angle', 'wave_spect_deviation', 'wave_spect_dir_components', 't', 'non_equil_boundary', 'tve', 'les_spec_name', 'rfg_number_of_modes', 'vm_number_of_vortices', 'vm_streamwise_fluct', 'vm_mass_conservation', 'volumetric_synthetic_turbulence_generator', 'volumetric_synthetic_turbulence_generator_option', 'volumetric_synthetic_turbulence_generator_option_thickness', 'ke_spec', 'nut', 'kl', 'intermit', 'k', 'e', 'o', 'v2', 'turb_intensity', 'turb_length_scale', 'turb_hydraulic_diam', 'turb_viscosity_ratio', 'turb_viscosity_ratio_profile', 'rst_spec', 'uu', 'vv', 'ww', 'uv', 'vw', 'uw', 'ksgs_spec', 'ksgs', 'sgs_turb_intensity', 'granular_temperature', 'iac', 'lsfun', 'volume_fraction', 'species_in_mole_fractions', 'mf', 'elec_potential_type', 'potential_value', 'dual_potential_type', 'dual_potential_value', 'x_displacement_type', 'x_displacement_value', 'y_displacement_type', 'y_displacement_value', 'z_displacement_type', 'z_displacement_value', 'prob_mode_1', 'prob_mode_2', 'prob_mode_3', 'equ_required', 'uds_bc', 'uds', 'pb_disc_bc', 'pb_disc', 'pb_qmom_bc', 'pb_qmom', 'pb_smm_bc', 'pb_smm', 'pb_dqmom_bc', 'pb_dqmom', 'p', 'premixc', 'premixc_var', 'ecfm_sigma', 'inert', 'pollut_no', 'pollut_hcn', 'pollut_nh3', 'pollut_n2o', 'pollut_urea', 'pollut_hnco', 'pollut_nco', 'pollut_so2', 'pollut_h2s', 'pollut_so3', 'pollut_sh', 'pollut_so', 'pollut_soot', 'pollut_nuclei', 'pollut_ctar', 'pollut_hg', 'pollut_hgcl2', 'pollut_hcl', 'pollut_hgo', 'pollut_cl', 'pollut_cl2', 'pollut_hgcl', 'pollut_hocl', 'radiation_bc', 'radial_direction_component', 'coll_dtheta', 'coll_dphi', 'band_q_irrad', 'band_q_irrad_diffuse', 'parallel_collimated_beam', 'solar_direction', 'solar_irradiation', 't_b_b_spec', 't_b_b', 'in_emiss', 'fmean', 'fvar', 'fmean2', 'fvar2', 'tss_scalar', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'fensapice_flow_bc_subtype', 'fensapice_drop_bccustom', 'fensapice_drop_lwc', 'fensapice_drop_dtemp', 'fensapice_drop_ddiam', 'fensapice_drop_dv', 'fensapice_drop_dx', 'fensapice_drop_dy', 'fensapice_drop_dz', 'fensapice_dpm_surface_injection', 'fensapice_dpm_inj_nstream', 'fensapice_drop_icc', 'fensapice_drop_ctemp', 'fensapice_drop_cdiam', 'fensapice_drop_cv', 'fensapice_drop_cx', 'fensapice_drop_cy', 'fensapice_drop_cz', 'fensapice_drop_vrh', 'fensapice_drop_vrh_1', 'fensapice_drop_vc', 'mixing_plane_thread', 'solar_fluxes', 'solar_shining_factor', 'radiating_s2s_surface', 'ac_options', 'impedance_0', 'impedance_1', 'impedance_2', 'ac_wave', 'les_spec']
    _child_classes = dict(
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        open_channel_wave_bc=open_channel_wave_bc,
        ocw_vel_segregated=ocw_vel_segregated,
        velocity_spec=velocity_spec,
        frame_of_reference=frame_of_reference,
        vmag=vmag,
        wave_velocity_spec=wave_velocity_spec,
        avg_flow_velocity=avg_flow_velocity,
        ocw_ship_vel_spec=ocw_ship_vel_spec,
        ocw_ship_vmag=ocw_ship_vmag,
        moving_object_direction_components=moving_object_direction_components,
        ocw_sp_vel_spec=ocw_sp_vel_spec,
        ocw_sp_vmag=ocw_sp_vmag,
        secondary_phase_direction_components=secondary_phase_direction_components,
        ocw_pp_vel_spec=ocw_pp_vel_spec,
        ocw_pp_ref_ht=ocw_pp_ref_ht,
        ocw_pp_power_coeff=ocw_pp_power_coeff,
        ocw_pp_vmag=ocw_pp_vmag,
        ocw_pp_vmag_ref=ocw_pp_vmag_ref,
        primary_phase_direction_components=primary_phase_direction_components,
        p_sup=p_sup,
        coordinate_system=coordinate_system,
        velocity_component=velocity_component,
        flow_direction_component=flow_direction_component,
        axis_direction_component=axis_direction_component_1,
        axis_origin_component=axis_origin_component_1,
        omega_swirl=omega_swirl,
        phase_spec=phase_spec,
        wave_bc_type=wave_bc_type,
        ht_local=ht_local,
        ht_bottom=ht_bottom,
        wave_dir_spec=wave_dir_spec,
        wave_modeling_type=wave_modeling_type,
        wave_list=wave_list,
        wave_list_shallow=wave_list_shallow,
        wave_spect_method_freq=wave_spect_method_freq,
        wave_spect_factor=wave_spect_factor,
        wave_spect_sig_wave_ht=wave_spect_sig_wave_ht,
        wave_spect_peak_freq=wave_spect_peak_freq,
        wave_spect_min_freq=wave_spect_min_freq,
        wave_spect_max_freq=wave_spect_max_freq,
        wave_spect_freq_components=wave_spect_freq_components,
        wave_spect_method_dir=wave_spect_method_dir,
        wave_spect_s=wave_spect_s,
        wave_spect_mean_angle=wave_spect_mean_angle,
        wave_spect_deviation=wave_spect_deviation,
        wave_spect_dir_components=wave_spect_dir_components,
        t=t,
        non_equil_boundary=non_equil_boundary,
        tve=tve,
        les_spec_name=les_spec_name,
        rfg_number_of_modes=rfg_number_of_modes,
        vm_number_of_vortices=vm_number_of_vortices,
        vm_streamwise_fluct=vm_streamwise_fluct,
        vm_mass_conservation=vm_mass_conservation,
        volumetric_synthetic_turbulence_generator=volumetric_synthetic_turbulence_generator,
        volumetric_synthetic_turbulence_generator_option=volumetric_synthetic_turbulence_generator_option,
        volumetric_synthetic_turbulence_generator_option_thickness=volumetric_synthetic_turbulence_generator_option_thickness,
        ke_spec=ke_spec,
        nut=nut,
        kl=kl,
        intermit=intermit,
        k=k,
        e=e,
        o=o,
        v2=v2,
        turb_intensity=turb_intensity,
        turb_length_scale=turb_length_scale,
        turb_hydraulic_diam=turb_hydraulic_diam,
        turb_viscosity_ratio=turb_viscosity_ratio,
        turb_viscosity_ratio_profile=turb_viscosity_ratio_profile,
        rst_spec=rst_spec,
        uu=uu,
        vv=vv,
        ww=ww,
        uv=uv,
        vw=vw,
        uw=uw,
        ksgs_spec=ksgs_spec,
        ksgs=ksgs,
        sgs_turb_intensity=sgs_turb_intensity,
        granular_temperature=granular_temperature,
        iac=iac,
        lsfun=lsfun,
        volume_fraction=volume_fraction,
        species_in_mole_fractions=species_in_mole_fractions,
        mf=mf,
        elec_potential_type=elec_potential_type,
        potential_value=potential_value,
        dual_potential_type=dual_potential_type,
        dual_potential_value=dual_potential_value,
        x_displacement_type=x_displacement_type,
        x_displacement_value=x_displacement_value,
        y_displacement_type=y_displacement_type,
        y_displacement_value=y_displacement_value,
        z_displacement_type=z_displacement_type,
        z_displacement_value=z_displacement_value,
        prob_mode_1=prob_mode_1,
        prob_mode_2=prob_mode_2,
        prob_mode_3=prob_mode_3,
        equ_required=equ_required,
        uds_bc=uds_bc,
        uds=uds,
        pb_disc_bc=pb_disc_bc,
        pb_disc=pb_disc_1,
        pb_qmom_bc=pb_qmom_bc,
        pb_qmom=pb_qmom,
        pb_smm_bc=pb_smm_bc,
        pb_smm=pb_smm,
        pb_dqmom_bc=pb_dqmom_bc,
        pb_dqmom=pb_dqmom,
        p=p,
        premixc=premixc,
        premixc_var=premixc_var,
        ecfm_sigma=ecfm_sigma,
        inert=inert,
        pollut_no=pollut_no,
        pollut_hcn=pollut_hcn,
        pollut_nh3=pollut_nh3,
        pollut_n2o=pollut_n2o,
        pollut_urea=pollut_urea,
        pollut_hnco=pollut_hnco,
        pollut_nco=pollut_nco,
        pollut_so2=pollut_so2,
        pollut_h2s=pollut_h2s,
        pollut_so3=pollut_so3,
        pollut_sh=pollut_sh,
        pollut_so=pollut_so,
        pollut_soot=pollut_soot,
        pollut_nuclei=pollut_nuclei,
        pollut_ctar=pollut_ctar,
        pollut_hg=pollut_hg,
        pollut_hgcl2=pollut_hgcl2,
        pollut_hcl=pollut_hcl,
        pollut_hgo=pollut_hgo,
        pollut_cl=pollut_cl,
        pollut_cl2=pollut_cl2,
        pollut_hgcl=pollut_hgcl,
        pollut_hocl=pollut_hocl,
        radiation_bc=radiation_bc,
        radial_direction_component=radial_direction_component,
        coll_dtheta=coll_dtheta,
        coll_dphi=coll_dphi,
        band_q_irrad=band_q_irrad,
        band_q_irrad_diffuse=band_q_irrad_diffuse,
        parallel_collimated_beam=parallel_collimated_beam,
        solar_direction=solar_direction,
        solar_irradiation=solar_irradiation,
        t_b_b_spec=t_b_b_spec,
        t_b_b=t_b_b,
        in_emiss=in_emiss,
        fmean=fmean,
        fvar=fvar,
        fmean2=fmean2,
        fvar2=fvar2,
        tss_scalar=tss_scalar,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        fensapice_flow_bc_subtype=fensapice_flow_bc_subtype,
        fensapice_drop_bccustom=fensapice_drop_bccustom,
        fensapice_drop_lwc=fensapice_drop_lwc,
        fensapice_drop_dtemp=fensapice_drop_dtemp,
        fensapice_drop_ddiam=fensapice_drop_ddiam,
        fensapice_drop_dv=fensapice_drop_dv,
        fensapice_drop_dx=fensapice_drop_dx,
        fensapice_drop_dy=fensapice_drop_dy,
        fensapice_drop_dz=fensapice_drop_dz,
        fensapice_dpm_surface_injection=fensapice_dpm_surface_injection,
        fensapice_dpm_inj_nstream=fensapice_dpm_inj_nstream,
        fensapice_drop_icc=fensapice_drop_icc,
        fensapice_drop_ctemp=fensapice_drop_ctemp,
        fensapice_drop_cdiam=fensapice_drop_cdiam,
        fensapice_drop_cv=fensapice_drop_cv,
        fensapice_drop_cx=fensapice_drop_cx,
        fensapice_drop_cy=fensapice_drop_cy,
        fensapice_drop_cz=fensapice_drop_cz,
        fensapice_drop_vrh=fensapice_drop_vrh,
        fensapice_drop_vrh_1=fensapice_drop_vrh_1,
        fensapice_drop_vc=fensapice_drop_vc,
        mixing_plane_thread=mixing_plane_thread,
        solar_fluxes=solar_fluxes,
        solar_shining_factor=solar_shining_factor,
        radiating_s2s_surface=radiating_s2s_surface,
        ac_options=ac_options,
        impedance_0=impedance_0,
        impedance_1=impedance_1,
        impedance_2=impedance_2,
        ac_wave=ac_wave,
        les_spec=les_spec,
    )
    return_type = 'object'

class phase_23(NamedObject[phase_23_child], CreatableNamedObjectMixinOld[phase_23_child]):
    """
    'phase' child.
    """
    _version = '222'
    fluent_name = 'phase'
    _python_name = 'phase'
    child_object_type = phase_23_child
    return_type = 'object'

class velocity_inlet_child(Group):
    """
    'child_object_type' of velocity_inlet.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'velocity_inlet_child'
    child_names = ['phase', 'geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'open_channel_wave_bc', 'ocw_vel_segregated', 'velocity_spec', 'frame_of_reference', 'vmag', 'wave_velocity_spec', 'avg_flow_velocity', 'ocw_ship_vel_spec', 'ocw_ship_vmag', 'moving_object_direction_components', 'ocw_sp_vel_spec', 'ocw_sp_vmag', 'secondary_phase_direction_components', 'ocw_pp_vel_spec', 'ocw_pp_ref_ht', 'ocw_pp_power_coeff', 'ocw_pp_vmag', 'ocw_pp_vmag_ref', 'primary_phase_direction_components', 'p_sup', 'coordinate_system', 'velocity_component', 'flow_direction_component', 'axis_direction_component', 'axis_origin_component', 'omega_swirl', 'phase_spec', 'wave_bc_type', 'ht_local', 'ht_bottom', 'wave_dir_spec', 'wave_modeling_type', 'wave_list', 'wave_list_shallow', 'wave_spect_method_freq', 'wave_spect_factor', 'wave_spect_sig_wave_ht', 'wave_spect_peak_freq', 'wave_spect_min_freq', 'wave_spect_max_freq', 'wave_spect_freq_components', 'wave_spect_method_dir', 'wave_spect_s', 'wave_spect_mean_angle', 'wave_spect_deviation', 'wave_spect_dir_components', 't', 'non_equil_boundary', 'tve', 'les_spec_name', 'rfg_number_of_modes', 'vm_number_of_vortices', 'vm_streamwise_fluct', 'vm_mass_conservation', 'volumetric_synthetic_turbulence_generator', 'volumetric_synthetic_turbulence_generator_option', 'volumetric_synthetic_turbulence_generator_option_thickness', 'ke_spec', 'nut', 'kl', 'intermit', 'k', 'e', 'o', 'v2', 'turb_intensity', 'turb_length_scale', 'turb_hydraulic_diam', 'turb_viscosity_ratio', 'turb_viscosity_ratio_profile', 'rst_spec', 'uu', 'vv', 'ww', 'uv', 'vw', 'uw', 'ksgs_spec', 'ksgs', 'sgs_turb_intensity', 'granular_temperature', 'iac', 'lsfun', 'volume_fraction', 'species_in_mole_fractions', 'mf', 'elec_potential_type', 'potential_value', 'dual_potential_type', 'dual_potential_value', 'x_displacement_type', 'x_displacement_value', 'y_displacement_type', 'y_displacement_value', 'z_displacement_type', 'z_displacement_value', 'prob_mode_1', 'prob_mode_2', 'prob_mode_3', 'equ_required', 'uds_bc', 'uds', 'pb_disc_bc', 'pb_disc', 'pb_qmom_bc', 'pb_qmom', 'pb_smm_bc', 'pb_smm', 'pb_dqmom_bc', 'pb_dqmom', 'p', 'premixc', 'premixc_var', 'ecfm_sigma', 'inert', 'pollut_no', 'pollut_hcn', 'pollut_nh3', 'pollut_n2o', 'pollut_urea', 'pollut_hnco', 'pollut_nco', 'pollut_so2', 'pollut_h2s', 'pollut_so3', 'pollut_sh', 'pollut_so', 'pollut_soot', 'pollut_nuclei', 'pollut_ctar', 'pollut_hg', 'pollut_hgcl2', 'pollut_hcl', 'pollut_hgo', 'pollut_cl', 'pollut_cl2', 'pollut_hgcl', 'pollut_hocl', 'radiation_bc', 'radial_direction_component', 'coll_dtheta', 'coll_dphi', 'band_q_irrad', 'band_q_irrad_diffuse', 'parallel_collimated_beam', 'solar_direction', 'solar_irradiation', 't_b_b_spec', 't_b_b', 'in_emiss', 'fmean', 'fvar', 'fmean2', 'fvar2', 'tss_scalar', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_udf', 'fensapice_flow_bc_subtype', 'fensapice_drop_bccustom', 'fensapice_drop_lwc', 'fensapice_drop_dtemp', 'fensapice_drop_ddiam', 'fensapice_drop_dv', 'fensapice_drop_dx', 'fensapice_drop_dy', 'fensapice_drop_dz', 'fensapice_dpm_surface_injection', 'fensapice_dpm_inj_nstream', 'fensapice_drop_icc', 'fensapice_drop_ctemp', 'fensapice_drop_cdiam', 'fensapice_drop_cv', 'fensapice_drop_cx', 'fensapice_drop_cy', 'fensapice_drop_cz', 'fensapice_drop_vrh', 'fensapice_drop_vrh_1', 'fensapice_drop_vc', 'mixing_plane_thread', 'solar_fluxes', 'solar_shining_factor', 'radiating_s2s_surface', 'ac_options', 'impedance_0', 'impedance_1', 'impedance_2', 'ac_wave', 'les_spec']
    _child_classes = dict(
        phase=phase_23,
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        open_channel_wave_bc=open_channel_wave_bc,
        ocw_vel_segregated=ocw_vel_segregated,
        velocity_spec=velocity_spec,
        frame_of_reference=frame_of_reference,
        vmag=vmag,
        wave_velocity_spec=wave_velocity_spec,
        avg_flow_velocity=avg_flow_velocity,
        ocw_ship_vel_spec=ocw_ship_vel_spec,
        ocw_ship_vmag=ocw_ship_vmag,
        moving_object_direction_components=moving_object_direction_components,
        ocw_sp_vel_spec=ocw_sp_vel_spec,
        ocw_sp_vmag=ocw_sp_vmag,
        secondary_phase_direction_components=secondary_phase_direction_components,
        ocw_pp_vel_spec=ocw_pp_vel_spec,
        ocw_pp_ref_ht=ocw_pp_ref_ht,
        ocw_pp_power_coeff=ocw_pp_power_coeff,
        ocw_pp_vmag=ocw_pp_vmag,
        ocw_pp_vmag_ref=ocw_pp_vmag_ref,
        primary_phase_direction_components=primary_phase_direction_components,
        p_sup=p_sup,
        coordinate_system=coordinate_system,
        velocity_component=velocity_component,
        flow_direction_component=flow_direction_component,
        axis_direction_component=axis_direction_component_1,
        axis_origin_component=axis_origin_component_1,
        omega_swirl=omega_swirl,
        phase_spec=phase_spec,
        wave_bc_type=wave_bc_type,
        ht_local=ht_local,
        ht_bottom=ht_bottom,
        wave_dir_spec=wave_dir_spec,
        wave_modeling_type=wave_modeling_type,
        wave_list=wave_list,
        wave_list_shallow=wave_list_shallow,
        wave_spect_method_freq=wave_spect_method_freq,
        wave_spect_factor=wave_spect_factor,
        wave_spect_sig_wave_ht=wave_spect_sig_wave_ht,
        wave_spect_peak_freq=wave_spect_peak_freq,
        wave_spect_min_freq=wave_spect_min_freq,
        wave_spect_max_freq=wave_spect_max_freq,
        wave_spect_freq_components=wave_spect_freq_components,
        wave_spect_method_dir=wave_spect_method_dir,
        wave_spect_s=wave_spect_s,
        wave_spect_mean_angle=wave_spect_mean_angle,
        wave_spect_deviation=wave_spect_deviation,
        wave_spect_dir_components=wave_spect_dir_components,
        t=t,
        non_equil_boundary=non_equil_boundary,
        tve=tve,
        les_spec_name=les_spec_name,
        rfg_number_of_modes=rfg_number_of_modes,
        vm_number_of_vortices=vm_number_of_vortices,
        vm_streamwise_fluct=vm_streamwise_fluct,
        vm_mass_conservation=vm_mass_conservation,
        volumetric_synthetic_turbulence_generator=volumetric_synthetic_turbulence_generator,
        volumetric_synthetic_turbulence_generator_option=volumetric_synthetic_turbulence_generator_option,
        volumetric_synthetic_turbulence_generator_option_thickness=volumetric_synthetic_turbulence_generator_option_thickness,
        ke_spec=ke_spec,
        nut=nut,
        kl=kl,
        intermit=intermit,
        k=k,
        e=e,
        o=o,
        v2=v2,
        turb_intensity=turb_intensity,
        turb_length_scale=turb_length_scale,
        turb_hydraulic_diam=turb_hydraulic_diam,
        turb_viscosity_ratio=turb_viscosity_ratio,
        turb_viscosity_ratio_profile=turb_viscosity_ratio_profile,
        rst_spec=rst_spec,
        uu=uu,
        vv=vv,
        ww=ww,
        uv=uv,
        vw=vw,
        uw=uw,
        ksgs_spec=ksgs_spec,
        ksgs=ksgs,
        sgs_turb_intensity=sgs_turb_intensity,
        granular_temperature=granular_temperature,
        iac=iac,
        lsfun=lsfun,
        volume_fraction=volume_fraction,
        species_in_mole_fractions=species_in_mole_fractions,
        mf=mf,
        elec_potential_type=elec_potential_type,
        potential_value=potential_value,
        dual_potential_type=dual_potential_type,
        dual_potential_value=dual_potential_value,
        x_displacement_type=x_displacement_type,
        x_displacement_value=x_displacement_value,
        y_displacement_type=y_displacement_type,
        y_displacement_value=y_displacement_value,
        z_displacement_type=z_displacement_type,
        z_displacement_value=z_displacement_value,
        prob_mode_1=prob_mode_1,
        prob_mode_2=prob_mode_2,
        prob_mode_3=prob_mode_3,
        equ_required=equ_required,
        uds_bc=uds_bc,
        uds=uds,
        pb_disc_bc=pb_disc_bc,
        pb_disc=pb_disc_1,
        pb_qmom_bc=pb_qmom_bc,
        pb_qmom=pb_qmom,
        pb_smm_bc=pb_smm_bc,
        pb_smm=pb_smm,
        pb_dqmom_bc=pb_dqmom_bc,
        pb_dqmom=pb_dqmom,
        p=p,
        premixc=premixc,
        premixc_var=premixc_var,
        ecfm_sigma=ecfm_sigma,
        inert=inert,
        pollut_no=pollut_no,
        pollut_hcn=pollut_hcn,
        pollut_nh3=pollut_nh3,
        pollut_n2o=pollut_n2o,
        pollut_urea=pollut_urea,
        pollut_hnco=pollut_hnco,
        pollut_nco=pollut_nco,
        pollut_so2=pollut_so2,
        pollut_h2s=pollut_h2s,
        pollut_so3=pollut_so3,
        pollut_sh=pollut_sh,
        pollut_so=pollut_so,
        pollut_soot=pollut_soot,
        pollut_nuclei=pollut_nuclei,
        pollut_ctar=pollut_ctar,
        pollut_hg=pollut_hg,
        pollut_hgcl2=pollut_hgcl2,
        pollut_hcl=pollut_hcl,
        pollut_hgo=pollut_hgo,
        pollut_cl=pollut_cl,
        pollut_cl2=pollut_cl2,
        pollut_hgcl=pollut_hgcl,
        pollut_hocl=pollut_hocl,
        radiation_bc=radiation_bc,
        radial_direction_component=radial_direction_component,
        coll_dtheta=coll_dtheta,
        coll_dphi=coll_dphi,
        band_q_irrad=band_q_irrad,
        band_q_irrad_diffuse=band_q_irrad_diffuse,
        parallel_collimated_beam=parallel_collimated_beam,
        solar_direction=solar_direction,
        solar_irradiation=solar_irradiation,
        t_b_b_spec=t_b_b_spec,
        t_b_b=t_b_b,
        in_emiss=in_emiss,
        fmean=fmean,
        fvar=fvar,
        fmean2=fmean2,
        fvar2=fvar2,
        tss_scalar=tss_scalar,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_udf=dpm_bc_udf,
        fensapice_flow_bc_subtype=fensapice_flow_bc_subtype,
        fensapice_drop_bccustom=fensapice_drop_bccustom,
        fensapice_drop_lwc=fensapice_drop_lwc,
        fensapice_drop_dtemp=fensapice_drop_dtemp,
        fensapice_drop_ddiam=fensapice_drop_ddiam,
        fensapice_drop_dv=fensapice_drop_dv,
        fensapice_drop_dx=fensapice_drop_dx,
        fensapice_drop_dy=fensapice_drop_dy,
        fensapice_drop_dz=fensapice_drop_dz,
        fensapice_dpm_surface_injection=fensapice_dpm_surface_injection,
        fensapice_dpm_inj_nstream=fensapice_dpm_inj_nstream,
        fensapice_drop_icc=fensapice_drop_icc,
        fensapice_drop_ctemp=fensapice_drop_ctemp,
        fensapice_drop_cdiam=fensapice_drop_cdiam,
        fensapice_drop_cv=fensapice_drop_cv,
        fensapice_drop_cx=fensapice_drop_cx,
        fensapice_drop_cy=fensapice_drop_cy,
        fensapice_drop_cz=fensapice_drop_cz,
        fensapice_drop_vrh=fensapice_drop_vrh,
        fensapice_drop_vrh_1=fensapice_drop_vrh_1,
        fensapice_drop_vc=fensapice_drop_vc,
        mixing_plane_thread=mixing_plane_thread,
        solar_fluxes=solar_fluxes,
        solar_shining_factor=solar_shining_factor,
        radiating_s2s_surface=radiating_s2s_surface,
        ac_options=ac_options,
        impedance_0=impedance_0,
        impedance_1=impedance_1,
        impedance_2=impedance_2,
        ac_wave=ac_wave,
        les_spec=les_spec,
    )
    return_type = 'object'

class velocity_inlet(NamedObject[velocity_inlet_child], CreatableNamedObjectMixinOld[velocity_inlet_child]):
    """
    'velocity_inlet' child.
    """
    _version = '222'
    fluent_name = 'velocity-inlet'
    _python_name = 'velocity_inlet'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = velocity_inlet_child
    return_type = 'object'

class d(Real, AllowedValuesMixin):
    """
    'd' child.
    """
    _version = '222'
    fluent_name = 'd'
    _python_name = 'd'
    return_type = 'object'

class q_dot(Group):
    """
    'q_dot' child.
    """
    _version = '222'
    fluent_name = 'q-dot'
    _python_name = 'q_dot'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class h(Group):
    """
    'h' child.
    """
    _version = '222'
    fluent_name = 'h'
    _python_name = 'h'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class tinf_1(Group):
    """
    'tinf' child.
    """
    _version = '222'
    fluent_name = 'tinf'
    _python_name = 'tinf'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class planar_conduction(Boolean, AllowedValuesMixin):
    """
    'planar_conduction' child.
    """
    _version = '222'
    fluent_name = 'planar-conduction?'
    _python_name = 'planar_conduction'
    return_type = 'object'

class thickness(Real, AllowedValuesMixin):
    """
    'thickness' child.
    """
    _version = '222'
    fluent_name = 'thickness'
    _python_name = 'thickness'
    return_type = 'object'

class qdot(Group):
    """
    'qdot' child.
    """
    _version = '222'
    fluent_name = 'qdot'
    _python_name = 'qdot'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class shell_conduction_child(Group):
    """
    'child_object_type' of shell_conduction.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'shell_conduction_child'
    child_names = ['thickness', 'material', 'qdot']
    _child_classes = dict(
        thickness=thickness,
        material=material,
        qdot=qdot,
    )
    return_type = 'object'

class shell_conduction(ListObject[shell_conduction_child]):
    """
    'shell_conduction' child.
    """
    _version = '222'
    fluent_name = 'shell-conduction'
    _python_name = 'shell_conduction'
    child_object_type = shell_conduction_child
    return_type = 'object'

class thin_wall_child(Group):
    """
    'child_object_type' of thin_wall.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'thin_wall_child'
    child_names = ['thickness', 'material', 'qdot']
    _child_classes = dict(
        thickness=thickness,
        material=material,
        qdot=qdot,
    )
    return_type = 'object'

class thin_wall(ListObject[thin_wall_child]):
    """
    'thin_wall' child.
    """
    _version = '222'
    fluent_name = 'thin-wall'
    _python_name = 'thin_wall'
    child_object_type = thin_wall_child
    return_type = 'object'

class motion_bc(String, AllowedValuesMixin):
    """
    'motion_bc' child.
    """
    _version = '222'
    fluent_name = 'motion-bc'
    _python_name = 'motion_bc'
    return_type = 'object'

class shear_bc(String, AllowedValuesMixin):
    """
    'shear_bc' child.
    """
    _version = '222'
    fluent_name = 'shear-bc'
    _python_name = 'shear_bc'
    return_type = 'object'

class rough_bc(String, AllowedValuesMixin):
    """
    'rough_bc' child.
    """
    _version = '222'
    fluent_name = 'rough-bc'
    _python_name = 'rough_bc'
    return_type = 'object'

class moving(Boolean, AllowedValuesMixin):
    """
    'moving' child.
    """
    _version = '222'
    fluent_name = 'moving?'
    _python_name = 'moving'
    return_type = 'object'

class relative(Boolean, AllowedValuesMixin):
    """
    'relative' child.
    """
    _version = '222'
    fluent_name = 'relative?'
    _python_name = 'relative'
    return_type = 'object'

class rotating(Boolean, AllowedValuesMixin):
    """
    'rotating' child.
    """
    _version = '222'
    fluent_name = 'rotating?'
    _python_name = 'rotating'
    return_type = 'object'

class component_of_wall_translation_child(Real, AllowedValuesMixin):
    """
    'child_object_type' of component_of_wall_translation.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'component_of_wall_translation_child'
    return_type = 'object'

class component_of_wall_translation(ListObject[component_of_wall_translation_child]):
    """
    'component_of_wall_translation' child.
    """
    _version = '222'
    fluent_name = 'component-of-wall-translation'
    _python_name = 'component_of_wall_translation'
    child_object_type = component_of_wall_translation_child
    return_type = 'object'

class components_1(Boolean, AllowedValuesMixin):
    """
    'components' child.
    """
    _version = '222'
    fluent_name = 'components?'
    _python_name = 'components'
    return_type = 'object'

class x_velocity(Group):
    """
    'x_velocity' child.
    """
    _version = '222'
    fluent_name = 'x-velocity'
    _python_name = 'x_velocity'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class y_velocity(Group):
    """
    'y_velocity' child.
    """
    _version = '222'
    fluent_name = 'y-velocity'
    _python_name = 'y_velocity'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class z_velocity(Group):
    """
    'z_velocity' child.
    """
    _version = '222'
    fluent_name = 'z-velocity'
    _python_name = 'z_velocity'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class velocity_components_child(Group):
    """
    'child_object_type' of velocity_components.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'velocity_components_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class velocity_components(ListObject[velocity_components_child]):
    """
    'velocity_components' child.
    """
    _version = '222'
    fluent_name = 'velocity-components'
    _python_name = 'velocity_components'
    child_object_type = velocity_components_child
    return_type = 'object'

class ex_emiss(Group):
    """
    'ex_emiss' child.
    """
    _version = '222'
    fluent_name = 'ex-emiss'
    _python_name = 'ex_emiss'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class trad(Group):
    """
    'trad' child.
    """
    _version = '222'
    fluent_name = 'trad'
    _python_name = 'trad'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class int_rad(Boolean, AllowedValuesMixin):
    """
    'int_rad' child.
    """
    _version = '222'
    fluent_name = 'int-rad?'
    _python_name = 'int_rad'
    return_type = 'object'

class trad_internal(Real, AllowedValuesMixin):
    """
    'trad_internal' child.
    """
    _version = '222'
    fluent_name = 'trad-internal'
    _python_name = 'trad_internal'
    return_type = 'object'

class area_enhancement_factor(Group):
    """
    'area_enhancement_factor' child.
    """
    _version = '222'
    fluent_name = 'area-enhancement-factor'
    _python_name = 'area_enhancement_factor'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class rough_option(Boolean, AllowedValuesMixin):
    """
    'rough_option' child.
    """
    _version = '222'
    fluent_name = 'rough-option?'
    _python_name = 'rough_option'
    return_type = 'object'

class rough_nasa(Boolean, AllowedValuesMixin):
    """
    'rough_nasa' child.
    """
    _version = '222'
    fluent_name = 'rough-nasa?'
    _python_name = 'rough_nasa'
    return_type = 'object'

class rough_shin_et_al(Boolean, AllowedValuesMixin):
    """
    'rough_shin_et_al' child.
    """
    _version = '222'
    fluent_name = 'rough-shin-et-al?'
    _python_name = 'rough_shin_et_al'
    return_type = 'object'

class rough_data(Boolean, AllowedValuesMixin):
    """
    'rough_data' child.
    """
    _version = '222'
    fluent_name = 'rough-data?'
    _python_name = 'rough_data'
    return_type = 'object'

class roughness_height(Group):
    """
    'roughness_height' child.
    """
    _version = '222'
    fluent_name = 'roughness-height'
    _python_name = 'roughness_height'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class roughness_const(Group):
    """
    'roughness_const' child.
    """
    _version = '222'
    fluent_name = 'roughness-const'
    _python_name = 'roughness_const'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class roughness_height_cp(Group):
    """
    'roughness_height_cp' child.
    """
    _version = '222'
    fluent_name = 'roughness-height-cp'
    _python_name = 'roughness_height_cp'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class roughness_const_cp(Group):
    """
    'roughness_const_cp' child.
    """
    _version = '222'
    fluent_name = 'roughness-const-cp'
    _python_name = 'roughness_const_cp'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class roughness_const_nasa(Group):
    """
    'roughness_const_nasa' child.
    """
    _version = '222'
    fluent_name = 'roughness-const-nasa'
    _python_name = 'roughness_const_nasa'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class roughness_const_shin(Group):
    """
    'roughness_const_shin' child.
    """
    _version = '222'
    fluent_name = 'roughness-const-shin'
    _python_name = 'roughness_const_shin'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class roughness_const_data(Group):
    """
    'roughness_const_data' child.
    """
    _version = '222'
    fluent_name = 'roughness-const-data'
    _python_name = 'roughness_const_data'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class variable_roughness(Group):
    """
    'variable_roughness' child.
    """
    _version = '222'
    fluent_name = 'variable-roughness'
    _python_name = 'variable_roughness'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class free_stream_velocity(Real, AllowedValuesMixin):
    """
    'free_stream_velocity' child.
    """
    _version = '222'
    fluent_name = 'free-stream-velocity'
    _python_name = 'free_stream_velocity'
    return_type = 'object'

class free_stream_temp(Real, AllowedValuesMixin):
    """
    'free_stream_temp' child.
    """
    _version = '222'
    fluent_name = 'free-stream-temp'
    _python_name = 'free_stream_temp'
    return_type = 'object'

class characteristic_length(Real, AllowedValuesMixin):
    """
    'characteristic_length' child.
    """
    _version = '222'
    fluent_name = 'characteristic-length'
    _python_name = 'characteristic_length'
    return_type = 'object'

class free_stream_temp_cp(Real, AllowedValuesMixin):
    """
    'free_stream_temp_cp' child.
    """
    _version = '222'
    fluent_name = 'free-stream-temp-cp'
    _python_name = 'free_stream_temp_cp'
    return_type = 'object'

class characteristic_length_cp(Real, AllowedValuesMixin):
    """
    'characteristic_length_cp' child.
    """
    _version = '222'
    fluent_name = 'characteristic-length-cp'
    _python_name = 'characteristic_length_cp'
    return_type = 'object'

class liquid_content(Group):
    """
    'liquid_content' child.
    """
    _version = '222'
    fluent_name = 'liquid-content'
    _python_name = 'liquid_content'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class liquid_content_cp(Group):
    """
    'liquid_content_cp' child.
    """
    _version = '222'
    fluent_name = 'liquid-content-cp'
    _python_name = 'liquid_content_cp'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class droplet_diameter(Group):
    """
    'droplet_diameter' child.
    """
    _version = '222'
    fluent_name = 'droplet-diameter'
    _python_name = 'droplet_diameter'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class dpm_bc_norm_coeff(Group):
    """
    'dpm_bc_norm_coeff' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-norm-coeff'
    _python_name = 'dpm_bc_norm_coeff'
    child_names = ['method', 'number_of_coeff', 'function_of', 'coefficients', 'constant', 'piecewise_polynomial', 'piecewise_linear']
    _child_classes = dict(
        method=method,
        number_of_coeff=number_of_coeff,
        function_of=function_of,
        coefficients=coefficients,
        constant=constant,
        piecewise_polynomial=piecewise_polynomial,
        piecewise_linear=piecewise_linear,
    )
    return_type = 'object'

class dpm_bc_tang_coeff(Group):
    """
    'dpm_bc_tang_coeff' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-tang-coeff'
    _python_name = 'dpm_bc_tang_coeff'
    child_names = ['method', 'number_of_coeff', 'function_of', 'coefficients', 'constant', 'piecewise_polynomial', 'piecewise_linear']
    _child_classes = dict(
        method=method,
        number_of_coeff=number_of_coeff,
        function_of=function_of,
        coefficients=coefficients,
        constant=constant,
        piecewise_polynomial=piecewise_polynomial,
        piecewise_linear=piecewise_linear,
    )
    return_type = 'object'

class dpm_bc_frictn_coeff(Group):
    """
    'dpm_bc_frictn_coeff' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-frictn-coeff'
    _python_name = 'dpm_bc_frictn_coeff'
    child_names = ['method', 'number_of_coeff', 'function_of', 'coefficients', 'constant', 'piecewise_polynomial', 'piecewise_linear']
    _child_classes = dict(
        method=method,
        number_of_coeff=number_of_coeff,
        function_of=function_of,
        coefficients=coefficients,
        constant=constant,
        piecewise_polynomial=piecewise_polynomial,
        piecewise_linear=piecewise_linear,
    )
    return_type = 'object'

class dpm_film_splash_nsamp(Integer, AllowedValuesMixin):
    """
    'dpm_film_splash_nsamp' child.
    """
    _version = '222'
    fluent_name = 'dpm-film-splash-nsamp'
    _python_name = 'dpm_film_splash_nsamp'
    return_type = 'object'

class dpm_crit_temp_option(String, AllowedValuesMixin):
    """
    'dpm_crit_temp_option' child.
    """
    _version = '222'
    fluent_name = 'dpm-crit-temp-option'
    _python_name = 'dpm_crit_temp_option'
    return_type = 'object'

class dpm_critical_temp_factor(Real, AllowedValuesMixin):
    """
    'dpm_critical_temp_factor' child.
    """
    _version = '222'
    fluent_name = 'dpm-critical-temp-factor'
    _python_name = 'dpm_critical_temp_factor'
    return_type = 'object'

class dpm_calibratable_temp(Real, AllowedValuesMixin):
    """
    'dpm_calibratable_temp' child.
    """
    _version = '222'
    fluent_name = 'dpm-calibratable-temp'
    _python_name = 'dpm_calibratable_temp'
    return_type = 'object'

class dpm_impingement_splashing_model(String, AllowedValuesMixin):
    """
    'dpm_impingement_splashing_model' child.
    """
    _version = '222'
    fluent_name = 'dpm-impingement-splashing-model'
    _python_name = 'dpm_impingement_splashing_model'
    return_type = 'object'

class dpm_upper_deposition_limit_offset(Real, AllowedValuesMixin):
    """
    'dpm_upper_deposition_limit_offset' child.
    """
    _version = '222'
    fluent_name = 'dpm-upper-deposition-limit-offset'
    _python_name = 'dpm_upper_deposition_limit_offset'
    return_type = 'object'

class dpm_deposition_delta_t(Real, AllowedValuesMixin):
    """
    'dpm_deposition_delta_t' child.
    """
    _version = '222'
    fluent_name = 'dpm-deposition-delta-t'
    _python_name = 'dpm_deposition_delta_t'
    return_type = 'object'

class dpm_laplace_number_constant(Real, AllowedValuesMixin):
    """
    'dpm_laplace_number_constant' child.
    """
    _version = '222'
    fluent_name = 'dpm-laplace-number-constant'
    _python_name = 'dpm_laplace_number_constant'
    return_type = 'object'

class dpm_partial_evaporation_ratio(Real, AllowedValuesMixin):
    """
    'dpm_partial_evaporation_ratio' child.
    """
    _version = '222'
    fluent_name = 'dpm-partial-evaporation-ratio'
    _python_name = 'dpm_partial_evaporation_ratio'
    return_type = 'object'

class ra_roughness(Real, AllowedValuesMixin):
    """
    'ra_roughness' child.
    """
    _version = '222'
    fluent_name = 'ra-roughness'
    _python_name = 'ra_roughness'
    return_type = 'object'

class rz_roughness(Real, AllowedValuesMixin):
    """
    'rz_roughness' child.
    """
    _version = '222'
    fluent_name = 'rz-roughness'
    _python_name = 'rz_roughness'
    return_type = 'object'

class rq_roughness(Real, AllowedValuesMixin):
    """
    'rq_roughness' child.
    """
    _version = '222'
    fluent_name = 'rq-roughness'
    _python_name = 'rq_roughness'
    return_type = 'object'

class rsm_roughness(Real, AllowedValuesMixin):
    """
    'rsm_roughness' child.
    """
    _version = '222'
    fluent_name = 'rsm-roughness'
    _python_name = 'rsm_roughness'
    return_type = 'object'

class dpm_bc_erosion_generic(Boolean, AllowedValuesMixin):
    """
    'dpm_bc_erosion_generic' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-generic?'
    _python_name = 'dpm_bc_erosion_generic'
    return_type = 'object'

class dpm_bc_erosion(Group):
    """
    'dpm_bc_erosion' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion'
    _python_name = 'dpm_bc_erosion'
    child_names = ['method', 'number_of_coeff', 'function_of', 'coefficients', 'constant', 'piecewise_polynomial', 'piecewise_linear']
    _child_classes = dict(
        method=method,
        number_of_coeff=number_of_coeff,
        function_of=function_of,
        coefficients=coefficients,
        constant=constant,
        piecewise_polynomial=piecewise_polynomial,
        piecewise_linear=piecewise_linear,
    )
    return_type = 'object'

class dpm_bc_erosion_c(Group):
    """
    'dpm_bc_erosion_c' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-c'
    _python_name = 'dpm_bc_erosion_c'
    child_names = ['method', 'number_of_coeff', 'function_of', 'coefficients', 'constant', 'piecewise_polynomial', 'piecewise_linear']
    _child_classes = dict(
        method=method,
        number_of_coeff=number_of_coeff,
        function_of=function_of,
        coefficients=coefficients,
        constant=constant,
        piecewise_polynomial=piecewise_polynomial,
        piecewise_linear=piecewise_linear,
    )
    return_type = 'object'

class dpm_bc_erosion_n(Group):
    """
    'dpm_bc_erosion_n' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-n'
    _python_name = 'dpm_bc_erosion_n'
    child_names = ['method', 'number_of_coeff', 'function_of', 'coefficients', 'constant', 'piecewise_polynomial', 'piecewise_linear']
    _child_classes = dict(
        method=method,
        number_of_coeff=number_of_coeff,
        function_of=function_of,
        coefficients=coefficients,
        constant=constant,
        piecewise_polynomial=piecewise_polynomial,
        piecewise_linear=piecewise_linear,
    )
    return_type = 'object'

class dpm_bc_erosion_finnie(Boolean, AllowedValuesMixin):
    """
    'dpm_bc_erosion_finnie' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-finnie?'
    _python_name = 'dpm_bc_erosion_finnie'
    return_type = 'object'

class dpm_bc_erosion_finnie_k(Real, AllowedValuesMixin):
    """
    'dpm_bc_erosion_finnie_k' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-finnie-k'
    _python_name = 'dpm_bc_erosion_finnie_k'
    return_type = 'object'

class dpm_bc_erosion_finnie_vel_exp(Real, AllowedValuesMixin):
    """
    'dpm_bc_erosion_finnie_vel_exp' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-finnie-vel-exp'
    _python_name = 'dpm_bc_erosion_finnie_vel_exp'
    return_type = 'object'

class dpm_bc_erosion_finnie_max_erosion_angle(Real, AllowedValuesMixin):
    """
    'dpm_bc_erosion_finnie_max_erosion_angle' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-finnie-max-erosion-angle'
    _python_name = 'dpm_bc_erosion_finnie_max_erosion_angle'
    return_type = 'object'

class dpm_bc_erosion_mclaury(Boolean, AllowedValuesMixin):
    """
    'dpm_bc_erosion_mclaury' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-mclaury?'
    _python_name = 'dpm_bc_erosion_mclaury'
    return_type = 'object'

class dpm_bc_erosion_mclaury_a(Real, AllowedValuesMixin):
    """
    'dpm_bc_erosion_mclaury_a' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-mclaury-a'
    _python_name = 'dpm_bc_erosion_mclaury_a'
    return_type = 'object'

class dpm_bc_erosion_mclaury_vel_exp(Real, AllowedValuesMixin):
    """
    'dpm_bc_erosion_mclaury_vel_exp' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-mclaury-vel-exp'
    _python_name = 'dpm_bc_erosion_mclaury_vel_exp'
    return_type = 'object'

class dpm_bc_erosion_mclaury_transition_angle(Real, AllowedValuesMixin):
    """
    'dpm_bc_erosion_mclaury_transition_angle' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-mclaury-transition-angle'
    _python_name = 'dpm_bc_erosion_mclaury_transition_angle'
    return_type = 'object'

class dpm_bc_erosion_mclaury_b(Real, AllowedValuesMixin):
    """
    'dpm_bc_erosion_mclaury_b' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-mclaury-b'
    _python_name = 'dpm_bc_erosion_mclaury_b'
    return_type = 'object'

class dpm_bc_erosion_mclaury_c(Real, AllowedValuesMixin):
    """
    'dpm_bc_erosion_mclaury_c' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-mclaury-c'
    _python_name = 'dpm_bc_erosion_mclaury_c'
    return_type = 'object'

class dpm_bc_erosion_mclaury_w(Real, AllowedValuesMixin):
    """
    'dpm_bc_erosion_mclaury_w' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-mclaury-w'
    _python_name = 'dpm_bc_erosion_mclaury_w'
    return_type = 'object'

class dpm_bc_erosion_mclaury_x(Real, AllowedValuesMixin):
    """
    'dpm_bc_erosion_mclaury_x' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-mclaury-x'
    _python_name = 'dpm_bc_erosion_mclaury_x'
    return_type = 'object'

class dpm_bc_erosion_mclaury_y(Real, AllowedValuesMixin):
    """
    'dpm_bc_erosion_mclaury_y' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-mclaury-y'
    _python_name = 'dpm_bc_erosion_mclaury_y'
    return_type = 'object'

class dpm_bc_erosion_oka(Boolean, AllowedValuesMixin):
    """
    'dpm_bc_erosion_oka' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-oka?'
    _python_name = 'dpm_bc_erosion_oka'
    return_type = 'object'

class dpm_bc_erosion_oka_e90(Real, AllowedValuesMixin):
    """
    'dpm_bc_erosion_oka_e90' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-oka-e90'
    _python_name = 'dpm_bc_erosion_oka_e90'
    return_type = 'object'

class dpm_bc_erosion_oka_hv(Real, AllowedValuesMixin):
    """
    'dpm_bc_erosion_oka_hv' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-oka-hv'
    _python_name = 'dpm_bc_erosion_oka_hv'
    return_type = 'object'

class dpm_bc_erosion_oka_n1(Real, AllowedValuesMixin):
    """
    'dpm_bc_erosion_oka_n1' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-oka-n1'
    _python_name = 'dpm_bc_erosion_oka_n1'
    return_type = 'object'

class dpm_bc_erosion_oka_n2(Real, AllowedValuesMixin):
    """
    'dpm_bc_erosion_oka_n2' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-oka-n2'
    _python_name = 'dpm_bc_erosion_oka_n2'
    return_type = 'object'

class dpm_bc_erosion_oka_k2(Real, AllowedValuesMixin):
    """
    'dpm_bc_erosion_oka_k2' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-oka-k2'
    _python_name = 'dpm_bc_erosion_oka_k2'
    return_type = 'object'

class dpm_bc_erosion_oka_k3(Real, AllowedValuesMixin):
    """
    'dpm_bc_erosion_oka_k3' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-oka-k3'
    _python_name = 'dpm_bc_erosion_oka_k3'
    return_type = 'object'

class dpm_bc_erosion_oka_dref(Real, AllowedValuesMixin):
    """
    'dpm_bc_erosion_oka_dref' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-oka-dref'
    _python_name = 'dpm_bc_erosion_oka_dref'
    return_type = 'object'

class dpm_bc_erosion_oka_vref(Real, AllowedValuesMixin):
    """
    'dpm_bc_erosion_oka_vref' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-oka-vref'
    _python_name = 'dpm_bc_erosion_oka_vref'
    return_type = 'object'

class dpm_bc_erosion_dnv(Boolean, AllowedValuesMixin):
    """
    'dpm_bc_erosion_dnv' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-dnv?'
    _python_name = 'dpm_bc_erosion_dnv'
    return_type = 'object'

class dpm_bc_erosion_dnv_k(Real, AllowedValuesMixin):
    """
    'dpm_bc_erosion_dnv_k' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-dnv-k'
    _python_name = 'dpm_bc_erosion_dnv_k'
    return_type = 'object'

class dpm_bc_erosion_dnv_n(Real, AllowedValuesMixin):
    """
    'dpm_bc_erosion_dnv_n' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-dnv-n'
    _python_name = 'dpm_bc_erosion_dnv_n'
    return_type = 'object'

class dpm_bc_erosion_dnv_ductile(Boolean, AllowedValuesMixin):
    """
    'dpm_bc_erosion_dnv_ductile' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-dnv-ductile?'
    _python_name = 'dpm_bc_erosion_dnv_ductile'
    return_type = 'object'

class dpm_bc_erosion_shear(Boolean, AllowedValuesMixin):
    """
    'dpm_bc_erosion_shear' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-shear?'
    _python_name = 'dpm_bc_erosion_shear'
    return_type = 'object'

class dpm_bc_erosion_shear_v(Real, AllowedValuesMixin):
    """
    'dpm_bc_erosion_shear_v' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-shear-v'
    _python_name = 'dpm_bc_erosion_shear_v'
    return_type = 'object'

class dpm_bc_erosion_shear_c(Real, AllowedValuesMixin):
    """
    'dpm_bc_erosion_shear_c' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-shear-c'
    _python_name = 'dpm_bc_erosion_shear_c'
    return_type = 'object'

class dpm_bc_erosion_shear_packing_limit(Real, AllowedValuesMixin):
    """
    'dpm_bc_erosion_shear_packing_limit' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-shear-packing-limit'
    _python_name = 'dpm_bc_erosion_shear_packing_limit'
    return_type = 'object'

class dpm_bc_erosion_shielding(Boolean, AllowedValuesMixin):
    """
    'dpm_bc_erosion_shielding' child.
    """
    _version = '222'
    fluent_name = 'dpm-bc-erosion-shielding?'
    _python_name = 'dpm_bc_erosion_shielding'
    return_type = 'object'

class dpm_wall_heat_exchange(Boolean, AllowedValuesMixin):
    """
    'dpm_wall_heat_exchange' child.
    """
    _version = '222'
    fluent_name = 'dpm-wall-heat-exchange?'
    _python_name = 'dpm_wall_heat_exchange'
    return_type = 'object'

class dpm_film_condensation(Boolean, AllowedValuesMixin):
    """
    'dpm_film_condensation' child.
    """
    _version = '222'
    fluent_name = 'dpm-film-condensation?'
    _python_name = 'dpm_film_condensation'
    return_type = 'object'

class dpm_film_bl_model(Boolean, AllowedValuesMixin):
    """
    'dpm_film_bl_model' child.
    """
    _version = '222'
    fluent_name = 'dpm-film-bl-model?'
    _python_name = 'dpm_film_bl_model'
    return_type = 'object'

class dpm_particle_stripping(Boolean, AllowedValuesMixin):
    """
    'dpm_particle_stripping' child.
    """
    _version = '222'
    fluent_name = 'dpm-particle-stripping?'
    _python_name = 'dpm_particle_stripping'
    return_type = 'object'

class dpm_critical_shear_stress(Real, AllowedValuesMixin):
    """
    'dpm_critical_shear_stress' child.
    """
    _version = '222'
    fluent_name = 'dpm-critical-shear-stress'
    _python_name = 'dpm_critical_shear_stress'
    return_type = 'object'

class dpm_film_separation_model(String, AllowedValuesMixin):
    """
    'dpm_film_separation_model' child.
    """
    _version = '222'
    fluent_name = 'dpm-film-separation-model'
    _python_name = 'dpm_film_separation_model'
    return_type = 'object'

class dpm_critical_we_number(Real, AllowedValuesMixin):
    """
    'dpm_critical_we_number' child.
    """
    _version = '222'
    fluent_name = 'dpm-critical-we-number'
    _python_name = 'dpm_critical_we_number'
    return_type = 'object'

class dpm_film_separation_angle(Real, AllowedValuesMixin):
    """
    'dpm_film_separation_angle' child.
    """
    _version = '222'
    fluent_name = 'dpm-film-separation-angle'
    _python_name = 'dpm_film_separation_angle'
    return_type = 'object'

class dpm_allow_lwf_to_vof(Boolean, AllowedValuesMixin):
    """
    'dpm_allow_lwf_to_vof' child.
    """
    _version = '222'
    fluent_name = 'dpm-allow-lwf-to-vof?'
    _python_name = 'dpm_allow_lwf_to_vof'
    return_type = 'object'

class dpm_allow_vof_to_lwf(Boolean, AllowedValuesMixin):
    """
    'dpm_allow_vof_to_lwf' child.
    """
    _version = '222'
    fluent_name = 'dpm-allow-vof-to-lwf?'
    _python_name = 'dpm_allow_vof_to_lwf'
    return_type = 'object'

class dpm_initialize_lwf(Boolean, AllowedValuesMixin):
    """
    'dpm_initialize_lwf' child.
    """
    _version = '222'
    fluent_name = 'dpm-initialize-lwf?'
    _python_name = 'dpm_initialize_lwf'
    return_type = 'object'

class dpm_initial_height(Real, AllowedValuesMixin):
    """
    'dpm_initial_height' child.
    """
    _version = '222'
    fluent_name = 'dpm-initial-height'
    _python_name = 'dpm_initial_height'
    return_type = 'object'

class film_velocity_child(Real, AllowedValuesMixin):
    """
    'child_object_type' of film_velocity.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'film_velocity_child'
    return_type = 'object'

class film_velocity(ListObject[film_velocity_child]):
    """
    'film_velocity' child.
    """
    _version = '222'
    fluent_name = 'film-velocity'
    _python_name = 'film_velocity'
    child_object_type = film_velocity_child
    return_type = 'object'

class dpm_initial_temperature(Real, AllowedValuesMixin):
    """
    'dpm_initial_temperature' child.
    """
    _version = '222'
    fluent_name = 'dpm-initial-temperature'
    _python_name = 'dpm_initial_temperature'
    return_type = 'object'

class dpm_initial_injection(String, AllowedValuesMixin):
    """
    'dpm_initial_injection' child.
    """
    _version = '222'
    fluent_name = 'dpm-initial-injection'
    _python_name = 'dpm_initial_injection'
    return_type = 'object'

class film_parcel_surface_area_density(Real, AllowedValuesMixin):
    """
    'film_parcel_surface_area_density' child.
    """
    _version = '222'
    fluent_name = 'film-parcel-surface-area-density'
    _python_name = 'film_parcel_surface_area_density'
    return_type = 'object'

class minimum_number_of_parcels_per_face(Integer, AllowedValuesMixin):
    """
    'minimum_number_of_parcels_per_face' child.
    """
    _version = '222'
    fluent_name = 'minimum-number-of-parcels-per-face'
    _python_name = 'minimum_number_of_parcels_per_face'
    return_type = 'object'

class band_in_emiss_child(Group):
    """
    'child_object_type' of band_in_emiss.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'band_in_emiss_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class band_in_emiss(NamedObject[band_in_emiss_child], CreatableNamedObjectMixinOld[band_in_emiss_child]):
    """
    'band_in_emiss' child.
    """
    _version = '222'
    fluent_name = 'band-in-emiss'
    _python_name = 'band_in_emiss'
    child_object_type = band_in_emiss_child
    return_type = 'object'

class mc_bsource_p(Boolean, AllowedValuesMixin):
    """
    'mc_bsource_p' child.
    """
    _version = '222'
    fluent_name = 'mc-bsource-p?'
    _python_name = 'mc_bsource_p'
    return_type = 'object'

class mc_poldfun_p(Boolean, AllowedValuesMixin):
    """
    'mc_poldfun_p' child.
    """
    _version = '222'
    fluent_name = 'mc-poldfun-p?'
    _python_name = 'mc_poldfun_p'
    return_type = 'object'

class polar_func_type(String, AllowedValuesMixin):
    """
    'polar_func_type' child.
    """
    _version = '222'
    fluent_name = 'polar-func-type'
    _python_name = 'polar_func_type'
    return_type = 'object'

class mc_polar_expr(Real, AllowedValuesMixin):
    """
    'mc_polar_expr' child.
    """
    _version = '222'
    fluent_name = 'mc-polar-expr'
    _python_name = 'mc_polar_expr'
    return_type = 'object'

class polar_real_angle(Real, AllowedValuesMixin):
    """
    'polar_real_angle' child.
    """
    _version = '222'
    fluent_name = 'polar-real-angle'
    _python_name = 'polar_real_angle'
    return_type = 'object'

class polar_real_intensity(Real, AllowedValuesMixin):
    """
    'polar_real_intensity' child.
    """
    _version = '222'
    fluent_name = 'polar-real-intensity'
    _python_name = 'polar_real_intensity'
    return_type = 'object'

class polar_pair_list_child(Group):
    """
    'child_object_type' of polar_pair_list.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'polar_pair_list_child'
    child_names = ['polar_real_angle', 'polar_real_intensity']
    _child_classes = dict(
        polar_real_angle=polar_real_angle,
        polar_real_intensity=polar_real_intensity,
    )
    return_type = 'object'

class polar_pair_list(ListObject[polar_pair_list_child]):
    """
    'polar_pair_list' child.
    """
    _version = '222'
    fluent_name = 'polar-pair-list'
    _python_name = 'polar_pair_list'
    child_object_type = polar_pair_list_child
    return_type = 'object'

class pold_pair_list_rad(Real, AllowedValuesMixin):
    """
    'pold_pair_list_rad' child.
    """
    _version = '222'
    fluent_name = 'pold-pair-list-rad'
    _python_name = 'pold_pair_list_rad'
    return_type = 'object'

class component_of_radiation_direction_child(Group):
    """
    'child_object_type' of component_of_radiation_direction.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'component_of_radiation_direction_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class component_of_radiation_direction(ListObject[component_of_radiation_direction_child]):
    """
    'component_of_radiation_direction' child.
    """
    _version = '222'
    fluent_name = 'component-of-radiation-direction'
    _python_name = 'component_of_radiation_direction'
    child_object_type = component_of_radiation_direction_child
    return_type = 'object'

class band_diffuse_frac_child(Real, AllowedValuesMixin):
    """
    'child_object_type' of band_diffuse_frac.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'band_diffuse_frac_child'
    return_type = 'object'

class band_diffuse_frac(NamedObject[band_diffuse_frac_child], CreatableNamedObjectMixinOld[band_diffuse_frac_child]):
    """
    'band_diffuse_frac' child.
    """
    _version = '222'
    fluent_name = 'band-diffuse-frac'
    _python_name = 'band_diffuse_frac'
    child_object_type = band_diffuse_frac_child
    return_type = 'object'

class critical_zone(Boolean, AllowedValuesMixin):
    """
    'critical_zone' child.
    """
    _version = '222'
    fluent_name = 'critical-zone?'
    _python_name = 'critical_zone'
    return_type = 'object'

class fpsc(Integer, AllowedValuesMixin):
    """
    'fpsc' child.
    """
    _version = '222'
    fluent_name = 'fpsc'
    _python_name = 'fpsc'
    return_type = 'object'

class v_transmissivity(Group):
    """
    'v_transmissivity' child.
    """
    _version = '222'
    fluent_name = 'v-transmissivity'
    _python_name = 'v_transmissivity'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class ir_transmissivity(Group):
    """
    'ir_transmissivity' child.
    """
    _version = '222'
    fluent_name = 'ir-transmissivity'
    _python_name = 'ir_transmissivity'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class v_opq_absorbtivity(Group):
    """
    'v_opq_absorbtivity' child.
    """
    _version = '222'
    fluent_name = 'v-opq-absorbtivity'
    _python_name = 'v_opq_absorbtivity'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class ir_opq_absorbtivity(Group):
    """
    'ir_opq_absorbtivity' child.
    """
    _version = '222'
    fluent_name = 'ir-opq-absorbtivity'
    _python_name = 'ir_opq_absorbtivity'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class v_st_absorbtivity(Group):
    """
    'v_st_absorbtivity' child.
    """
    _version = '222'
    fluent_name = 'v-st-absorbtivity'
    _python_name = 'v_st_absorbtivity'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class ir_st_absorbtivity(Group):
    """
    'ir_st_absorbtivity' child.
    """
    _version = '222'
    fluent_name = 'ir-st-absorbtivity'
    _python_name = 'ir_st_absorbtivity'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class d_st_absorbtivity(Group):
    """
    'd_st_absorbtivity' child.
    """
    _version = '222'
    fluent_name = 'd-st-absorbtivity'
    _python_name = 'd_st_absorbtivity'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class d_transmissivity(Group):
    """
    'd_transmissivity' child.
    """
    _version = '222'
    fluent_name = 'd-transmissivity'
    _python_name = 'd_transmissivity'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class fsi_interface(Boolean, AllowedValuesMixin):
    """
    'fsi_interface' child.
    """
    _version = '222'
    fluent_name = 'fsi-interface?'
    _python_name = 'fsi_interface'
    return_type = 'object'

class partially_catalytic(Boolean, AllowedValuesMixin):
    """
    'partially_catalytic' child.
    """
    _version = '222'
    fluent_name = 'partially-catalytic?'
    _python_name = 'partially_catalytic'
    return_type = 'object'

class partially_catalytic_material(String, AllowedValuesMixin):
    """
    'partially_catalytic_material' child.
    """
    _version = '222'
    fluent_name = 'partially-catalytic-material'
    _python_name = 'partially_catalytic_material'
    return_type = 'object'

class partially_catalytic_recombination_coefficient_o(Group):
    """
    'partially_catalytic_recombination_coefficient_o' child.
    """
    _version = '222'
    fluent_name = 'partially-catalytic-recombination-coefficient-o'
    _python_name = 'partially_catalytic_recombination_coefficient_o'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class partially_catalytic_recombination_coefficient_n(Group):
    """
    'partially_catalytic_recombination_coefficient_n' child.
    """
    _version = '222'
    fluent_name = 'partially-catalytic-recombination-coefficient-n'
    _python_name = 'partially_catalytic_recombination_coefficient_n'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class partially_catalytic_recombination_model(String, AllowedValuesMixin):
    """
    'partially_catalytic_recombination_model' child.
    """
    _version = '222'
    fluent_name = 'partially-catalytic-recombination-model'
    _python_name = 'partially_catalytic_recombination_model'
    return_type = 'object'

class species_spec_child(String, AllowedValuesMixin):
    """
    'child_object_type' of species_spec.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'species_spec_child'
    return_type = 'object'

class species_spec(NamedObject[species_spec_child], CreatableNamedObjectMixinOld[species_spec_child]):
    """
    'species_spec' child.
    """
    _version = '222'
    fluent_name = 'species-spec'
    _python_name = 'species_spec'
    child_object_type = species_spec_child
    return_type = 'object'

class elec_potential_jump(Group):
    """
    'elec_potential_jump' child.
    """
    _version = '222'
    fluent_name = 'elec-potential-jump'
    _python_name = 'elec_potential_jump'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class elec_potential_resistance(Group):
    """
    'elec_potential_resistance' child.
    """
    _version = '222'
    fluent_name = 'elec-potential-resistance'
    _python_name = 'elec_potential_resistance'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class echem_reaction(Boolean, AllowedValuesMixin):
    """
    'echem_reaction' child.
    """
    _version = '222'
    fluent_name = 'echem-reaction?'
    _python_name = 'echem_reaction'
    return_type = 'object'

class elec_potential_mechs(String, AllowedValuesMixin):
    """
    'elec_potential_mechs' child.
    """
    _version = '222'
    fluent_name = 'elec-potential-mechs'
    _python_name = 'elec_potential_mechs'
    return_type = 'object'

class faradaic_heat(Boolean, AllowedValuesMixin):
    """
    'faradaic_heat' child.
    """
    _version = '222'
    fluent_name = 'faradaic-heat?'
    _python_name = 'faradaic_heat'
    return_type = 'object'

class li_ion_type(String, AllowedValuesMixin):
    """
    'li_ion_type' child.
    """
    _version = '222'
    fluent_name = 'li-ion-type'
    _python_name = 'li_ion_type'
    return_type = 'object'

class li_ion_value(Group):
    """
    'li_ion_value' child.
    """
    _version = '222'
    fluent_name = 'li-ion-value'
    _python_name = 'li_ion_value'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class per_dispx(Group):
    """
    'per_dispx' child.
    """
    _version = '222'
    fluent_name = 'per-dispx'
    _python_name = 'per_dispx'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class per_dispy(Group):
    """
    'per_dispy' child.
    """
    _version = '222'
    fluent_name = 'per-dispy'
    _python_name = 'per_dispy'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class per_dispz(Group):
    """
    'per_dispz' child.
    """
    _version = '222'
    fluent_name = 'per-dispz'
    _python_name = 'per_dispz'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class per_imagx(Group):
    """
    'per_imagx' child.
    """
    _version = '222'
    fluent_name = 'per-imagx'
    _python_name = 'per_imagx'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class per_imagy(Group):
    """
    'per_imagy' child.
    """
    _version = '222'
    fluent_name = 'per-imagy'
    _python_name = 'per_imagy'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class per_imagz(Group):
    """
    'per_imagz' child.
    """
    _version = '222'
    fluent_name = 'per-imagz'
    _python_name = 'per_imagz'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class freq(Group):
    """
    'freq' child.
    """
    _version = '222'
    fluent_name = 'freq'
    _python_name = 'freq'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class amp(Group):
    """
    'amp' child.
    """
    _version = '222'
    fluent_name = 'amp'
    _python_name = 'amp'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class nodal_diam(Integer, AllowedValuesMixin):
    """
    'nodal_diam' child.
    """
    _version = '222'
    fluent_name = 'nodal-diam'
    _python_name = 'nodal_diam'
    return_type = 'object'

class pass_number(Group):
    """
    'pass_number' child.
    """
    _version = '222'
    fluent_name = 'pass-number'
    _python_name = 'pass_number'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class fwd(Boolean, AllowedValuesMixin):
    """
    'fwd' child.
    """
    _version = '222'
    fluent_name = 'fwd?'
    _python_name = 'fwd'
    return_type = 'object'

class aero(Boolean, AllowedValuesMixin):
    """
    'aero' child.
    """
    _version = '222'
    fluent_name = 'aero?'
    _python_name = 'aero'
    return_type = 'object'

class cmplx(Boolean, AllowedValuesMixin):
    """
    'cmplx' child.
    """
    _version = '222'
    fluent_name = 'cmplx?'
    _python_name = 'cmplx'
    return_type = 'object'

class norm(Boolean, AllowedValuesMixin):
    """
    'norm' child.
    """
    _version = '222'
    fluent_name = 'norm?'
    _python_name = 'norm'
    return_type = 'object'

class method_1(Integer, AllowedValuesMixin):
    """
    'method' child.
    """
    _version = '222'
    fluent_name = 'method?'
    _python_name = 'method'
    return_type = 'object'

class gtemp_bc(String, AllowedValuesMixin):
    """
    'gtemp_bc' child.
    """
    _version = '222'
    fluent_name = 'gtemp-bc'
    _python_name = 'gtemp_bc'
    return_type = 'object'

class g_temperature(Group):
    """
    'g_temperature' child.
    """
    _version = '222'
    fluent_name = 'g-temperature'
    _python_name = 'g_temperature'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class g_qflux(Group):
    """
    'g_qflux' child.
    """
    _version = '222'
    fluent_name = 'g-qflux'
    _python_name = 'g_qflux'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class wall_restitution_coeff(Real, AllowedValuesMixin):
    """
    'wall_restitution_coeff' child.
    """
    _version = '222'
    fluent_name = 'wall-restitution-coeff'
    _python_name = 'wall_restitution_coeff'
    return_type = 'object'

class origin_position_of_rotation_axis_child(Real, AllowedValuesMixin):
    """
    'child_object_type' of origin_position_of_rotation_axis.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'origin_position_of_rotation_axis_child'
    return_type = 'object'

class origin_position_of_rotation_axis(ListObject[origin_position_of_rotation_axis_child]):
    """
    'origin_position_of_rotation_axis' child.
    """
    _version = '222'
    fluent_name = 'origin-position-of-rotation-axis'
    _python_name = 'origin_position_of_rotation_axis'
    child_object_type = origin_position_of_rotation_axis_child
    return_type = 'object'

class direction_component_of_rotation_axis_child(Real, AllowedValuesMixin):
    """
    'child_object_type' of direction_component_of_rotation_axis.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'direction_component_of_rotation_axis_child'
    return_type = 'object'

class direction_component_of_rotation_axis(ListObject[direction_component_of_rotation_axis_child]):
    """
    'direction_component_of_rotation_axis' child.
    """
    _version = '222'
    fluent_name = 'direction-component-of-rotation-axis'
    _python_name = 'direction_component_of_rotation_axis'
    child_object_type = direction_component_of_rotation_axis_child
    return_type = 'object'

class specified_shear(Boolean, AllowedValuesMixin):
    """
    'specified_shear' child.
    """
    _version = '222'
    fluent_name = 'specified-shear?'
    _python_name = 'specified_shear'
    return_type = 'object'

class shear_y(Group):
    """
    'shear_y' child.
    """
    _version = '222'
    fluent_name = 'shear-y'
    _python_name = 'shear_y'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class shear_z(Group):
    """
    'shear_z' child.
    """
    _version = '222'
    fluent_name = 'shear-z'
    _python_name = 'shear_z'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class shear_stress_components_child(Group):
    """
    'child_object_type' of shear_stress_components.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'shear_stress_components_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class shear_stress_components(ListObject[shear_stress_components_child]):
    """
    'shear_stress_components' child.
    """
    _version = '222'
    fluent_name = 'shear-stress-components'
    _python_name = 'shear_stress_components'
    child_object_type = shear_stress_components_child
    return_type = 'object'

class fslip(Real, AllowedValuesMixin):
    """
    'fslip' child.
    """
    _version = '222'
    fluent_name = 'fslip'
    _python_name = 'fslip'
    return_type = 'object'

class eslip(Real, AllowedValuesMixin):
    """
    'eslip' child.
    """
    _version = '222'
    fluent_name = 'eslip'
    _python_name = 'eslip'
    return_type = 'object'

class surf_tens_grad(Real, AllowedValuesMixin):
    """
    'surf_tens_grad' child.
    """
    _version = '222'
    fluent_name = 'surf-tens-grad'
    _python_name = 'surf_tens_grad'
    return_type = 'object'

class contact_resistance(Group):
    """
    'contact_resistance' child.
    """
    _version = '222'
    fluent_name = 'contact-resistance'
    _python_name = 'contact_resistance'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class surf_washcoat_factor(Real, AllowedValuesMixin):
    """
    'surf_washcoat_factor' child.
    """
    _version = '222'
    fluent_name = 'surf-washcoat-factor'
    _python_name = 'surf_washcoat_factor'
    return_type = 'object'

class ablation_select_model(String, AllowedValuesMixin):
    """
    'ablation_select_model' child.
    """
    _version = '222'
    fluent_name = 'ablation-select-model'
    _python_name = 'ablation_select_model'
    return_type = 'object'

class ablation_vielle_a(Real, AllowedValuesMixin):
    """
    'ablation_vielle_a' child.
    """
    _version = '222'
    fluent_name = 'ablation-vielle-a'
    _python_name = 'ablation_vielle_a'
    return_type = 'object'

class ablation_vielle_n(Real, AllowedValuesMixin):
    """
    'ablation_vielle_n' child.
    """
    _version = '222'
    fluent_name = 'ablation-vielle-n'
    _python_name = 'ablation_vielle_n'
    return_type = 'object'

class ablation_surfacerxn_density(Real, AllowedValuesMixin):
    """
    'ablation_surfacerxn_density' child.
    """
    _version = '222'
    fluent_name = 'ablation-surfacerxn-density'
    _python_name = 'ablation_surfacerxn_density'
    return_type = 'object'

class ablation_flux(Boolean, AllowedValuesMixin):
    """
    'ablation_flux' child.
    """
    _version = '222'
    fluent_name = 'ablation-flux?'
    _python_name = 'ablation_flux'
    return_type = 'object'

class ablation_species_mf_child(Group):
    """
    'child_object_type' of ablation_species_mf.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'ablation_species_mf_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class ablation_species_mf(NamedObject[ablation_species_mf_child], CreatableNamedObjectMixinOld[ablation_species_mf_child]):
    """
    'ablation_species_mf' child.
    """
    _version = '222'
    fluent_name = 'ablation-species-mf'
    _python_name = 'ablation_species_mf'
    child_object_type = ablation_species_mf_child
    return_type = 'object'

class specular_coeff(Real, AllowedValuesMixin):
    """
    'specular_coeff' child.
    """
    _version = '222'
    fluent_name = 'specular-coeff'
    _python_name = 'specular_coeff'
    return_type = 'object'

class mom_accom_coef(Real, AllowedValuesMixin):
    """
    'mom_accom_coef' child.
    """
    _version = '222'
    fluent_name = 'mom-accom-coef'
    _python_name = 'mom_accom_coef'
    return_type = 'object'

class therm_accom_coef(Real, AllowedValuesMixin):
    """
    'therm_accom_coef' child.
    """
    _version = '222'
    fluent_name = 'therm-accom-coef'
    _python_name = 'therm_accom_coef'
    return_type = 'object'

class eve_accom_coef(Real, AllowedValuesMixin):
    """
    'eve_accom_coef' child.
    """
    _version = '222'
    fluent_name = 'eve-accom-coef'
    _python_name = 'eve_accom_coef'
    return_type = 'object'

class film_wall(Boolean, AllowedValuesMixin):
    """
    'film_wall' child.
    """
    _version = '222'
    fluent_name = 'film-wall?'
    _python_name = 'film_wall'
    return_type = 'object'

class film_wall_bc(String, AllowedValuesMixin):
    """
    'film_wall_bc' child.
    """
    _version = '222'
    fluent_name = 'film-wall-bc'
    _python_name = 'film_wall_bc'
    return_type = 'object'

class film_height(Group):
    """
    'film_height' child.
    """
    _version = '222'
    fluent_name = 'film-height'
    _python_name = 'film_height'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class flux_momentum_components_child(Group):
    """
    'child_object_type' of flux_momentum_components.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'flux_momentum_components_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class flux_momentum_components(ListObject[flux_momentum_components_child]):
    """
    'flux_momentum_components' child.
    """
    _version = '222'
    fluent_name = 'flux-momentum-components'
    _python_name = 'flux_momentum_components'
    child_object_type = flux_momentum_components_child
    return_type = 'object'

class film_relative_vel(Boolean, AllowedValuesMixin):
    """
    'film_relative_vel' child.
    """
    _version = '222'
    fluent_name = 'film-relative-vel?'
    _python_name = 'film_relative_vel'
    return_type = 'object'

class film_bc_imp_press(Boolean, AllowedValuesMixin):
    """
    'film_bc_imp_press' child.
    """
    _version = '222'
    fluent_name = 'film-bc-imp-press?'
    _python_name = 'film_bc_imp_press'
    return_type = 'object'

class film_temperature(Group):
    """
    'film_temperature' child.
    """
    _version = '222'
    fluent_name = 'film-temperature'
    _python_name = 'film_temperature'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class film_scalar(Group):
    """
    'film_scalar' child.
    """
    _version = '222'
    fluent_name = 'film-scalar'
    _python_name = 'film_scalar'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class film_source(Boolean, AllowedValuesMixin):
    """
    'film_source' child.
    """
    _version = '222'
    fluent_name = 'film-source?'
    _python_name = 'film_source'
    return_type = 'object'

class film_h_src(Group):
    """
    'film_h_src' child.
    """
    _version = '222'
    fluent_name = 'film-h-src'
    _python_name = 'film_h_src'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class film_u_src(Group):
    """
    'film_u_src' child.
    """
    _version = '222'
    fluent_name = 'film-u-src'
    _python_name = 'film_u_src'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class film_v_src(Group):
    """
    'film_v_src' child.
    """
    _version = '222'
    fluent_name = 'film-v-src'
    _python_name = 'film_v_src'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class film_w_src(Group):
    """
    'film_w_src' child.
    """
    _version = '222'
    fluent_name = 'film-w-src'
    _python_name = 'film_w_src'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class momentum_source_components_child(Group):
    """
    'child_object_type' of momentum_source_components.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'momentum_source_components_child'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class momentum_source_components(ListObject[momentum_source_components_child]):
    """
    'momentum_source_components' child.
    """
    _version = '222'
    fluent_name = 'momentum-source-components'
    _python_name = 'momentum_source_components'
    child_object_type = momentum_source_components_child
    return_type = 'object'

class film_t_src(Group):
    """
    'film_t_src' child.
    """
    _version = '222'
    fluent_name = 'film-t-src'
    _python_name = 'film_t_src'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class film_s_src(Group):
    """
    'film_s_src' child.
    """
    _version = '222'
    fluent_name = 'film-s-src'
    _python_name = 'film_s_src'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class film_phase_change(Boolean, AllowedValuesMixin):
    """
    'film_phase_change' child.
    """
    _version = '222'
    fluent_name = 'film-phase-change?'
    _python_name = 'film_phase_change'
    return_type = 'object'

class film_phase_change_model(String, AllowedValuesMixin):
    """
    'film_phase_change_model' child.
    """
    _version = '222'
    fluent_name = 'film-phase-change-model'
    _python_name = 'film_phase_change_model'
    return_type = 'object'

class film_cond_const(Real, AllowedValuesMixin):
    """
    'film_cond_const' child.
    """
    _version = '222'
    fluent_name = 'film-cond-const'
    _python_name = 'film_cond_const'
    return_type = 'object'

class film_vapo_const(Real, AllowedValuesMixin):
    """
    'film_vapo_const' child.
    """
    _version = '222'
    fluent_name = 'film-vapo-const'
    _python_name = 'film_vapo_const'
    return_type = 'object'

class film_cond_rate(Group):
    """
    'film_cond_rate' child.
    """
    _version = '222'
    fluent_name = 'film-cond-rate'
    _python_name = 'film_cond_rate'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class film_vapo_rate(Group):
    """
    'film_vapo_rate' child.
    """
    _version = '222'
    fluent_name = 'film-vapo-rate'
    _python_name = 'film_vapo_rate'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class film_momentum_coupling(Boolean, AllowedValuesMixin):
    """
    'film_momentum_coupling' child.
    """
    _version = '222'
    fluent_name = 'film-momentum-coupling?'
    _python_name = 'film_momentum_coupling'
    return_type = 'object'

class film_splash_wall(Boolean, AllowedValuesMixin):
    """
    'film_splash_wall' child.
    """
    _version = '222'
    fluent_name = 'film-splash-wall?'
    _python_name = 'film_splash_wall'
    return_type = 'object'

class film_boundary_separation(Boolean, AllowedValuesMixin):
    """
    'film_boundary_separation' child.
    """
    _version = '222'
    fluent_name = 'film-boundary-separation?'
    _python_name = 'film_boundary_separation'
    return_type = 'object'

class film_impinge_model(String, AllowedValuesMixin):
    """
    'film_impinge_model' child.
    """
    _version = '222'
    fluent_name = 'film-impinge-model'
    _python_name = 'film_impinge_model'
    return_type = 'object'

class film_splash_nparc(Integer, AllowedValuesMixin):
    """
    'film_splash_nparc' child.
    """
    _version = '222'
    fluent_name = 'film-splash-nparc'
    _python_name = 'film_splash_nparc'
    return_type = 'object'

class film_crit_temp_factor(Real, AllowedValuesMixin):
    """
    'film_crit_temp_factor' child.
    """
    _version = '222'
    fluent_name = 'film-crit-temp-factor'
    _python_name = 'film_crit_temp_factor'
    return_type = 'object'

class film_roughness_ra(Real, AllowedValuesMixin):
    """
    'film_roughness_ra' child.
    """
    _version = '222'
    fluent_name = 'film-roughness-ra'
    _python_name = 'film_roughness_ra'
    return_type = 'object'

class film_roughness_rz(Real, AllowedValuesMixin):
    """
    'film_roughness_rz' child.
    """
    _version = '222'
    fluent_name = 'film-roughness-rz'
    _python_name = 'film_roughness_rz'
    return_type = 'object'

class film_upper_deposition_limit_offset(Real, AllowedValuesMixin):
    """
    'film_upper_deposition_limit_offset' child.
    """
    _version = '222'
    fluent_name = 'film-upper-deposition-limit-offset'
    _python_name = 'film_upper_deposition_limit_offset'
    return_type = 'object'

class film_deposition_delta_t(Real, AllowedValuesMixin):
    """
    'film_deposition_delta_t' child.
    """
    _version = '222'
    fluent_name = 'film-deposition-delta-t'
    _python_name = 'film_deposition_delta_t'
    return_type = 'object'

class film_laplace_number_constant(Real, AllowedValuesMixin):
    """
    'film_laplace_number_constant' child.
    """
    _version = '222'
    fluent_name = 'film-laplace-number-constant'
    _python_name = 'film_laplace_number_constant'
    return_type = 'object'

class film_partial_evap_ratio(Real, AllowedValuesMixin):
    """
    'film_partial_evap_ratio' child.
    """
    _version = '222'
    fluent_name = 'film-partial-evap-ratio'
    _python_name = 'film_partial_evap_ratio'
    return_type = 'object'

class film_contact_angle(Boolean, AllowedValuesMixin):
    """
    'film_contact_angle' child.
    """
    _version = '222'
    fluent_name = 'film-contact-angle?'
    _python_name = 'film_contact_angle'
    return_type = 'object'

class film_contact_angle_mean(Group):
    """
    'film_contact_angle_mean' child.
    """
    _version = '222'
    fluent_name = 'film-contact-angle-mean'
    _python_name = 'film_contact_angle_mean'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class film_contact_angle_rstd(Real, AllowedValuesMixin):
    """
    'film_contact_angle_rstd' child.
    """
    _version = '222'
    fluent_name = 'film-contact-angle-rstd'
    _python_name = 'film_contact_angle_rstd'
    return_type = 'object'

class film_contact_angle_beta(Real, AllowedValuesMixin):
    """
    'film_contact_angle_beta' child.
    """
    _version = '222'
    fluent_name = 'film-contact-angle-beta'
    _python_name = 'film_contact_angle_beta'
    return_type = 'object'

class film_vof_coupling_high(Boolean, AllowedValuesMixin):
    """
    'film_vof_coupling_high' child.
    """
    _version = '222'
    fluent_name = 'film-vof-coupling-high?'
    _python_name = 'film_vof_coupling_high'
    return_type = 'object'

class film_vof_trans_high(Real, AllowedValuesMixin):
    """
    'film_vof_trans_high' child.
    """
    _version = '222'
    fluent_name = 'film-vof-trans-high'
    _python_name = 'film_vof_trans_high'
    return_type = 'object'

class film_vof_trans_high_relax(Real, AllowedValuesMixin):
    """
    'film_vof_trans_high_relax' child.
    """
    _version = '222'
    fluent_name = 'film-vof-trans-high-relax'
    _python_name = 'film_vof_trans_high_relax'
    return_type = 'object'

class film_vof_coupling_low(Boolean, AllowedValuesMixin):
    """
    'film_vof_coupling_low' child.
    """
    _version = '222'
    fluent_name = 'film-vof-coupling-low?'
    _python_name = 'film_vof_coupling_low'
    return_type = 'object'

class film_vof_trans_low(Real, AllowedValuesMixin):
    """
    'film_vof_trans_low' child.
    """
    _version = '222'
    fluent_name = 'film-vof-trans-low'
    _python_name = 'film_vof_trans_low'
    return_type = 'object'

class film_vof_trans_low_relax(Real, AllowedValuesMixin):
    """
    'film_vof_trans_low_relax' child.
    """
    _version = '222'
    fluent_name = 'film-vof-trans-low-relax'
    _python_name = 'film_vof_trans_low_relax'
    return_type = 'object'

class caf(Group):
    """
    'caf' child.
    """
    _version = '222'
    fluent_name = 'caf'
    _python_name = 'caf'
    child_names = ['option', 'constant', 'profile_name', 'field_name', 'udf']
    _child_classes = dict(
        option=option,
        constant=constant,
        profile_name=profile_name,
        field_name=field_name,
        udf=udf,
    )
    return_type = 'object'

class thermal_stabilization(Boolean, AllowedValuesMixin):
    """
    'thermal_stabilization' child.
    """
    _version = '222'
    fluent_name = 'thermal-stabilization?'
    _python_name = 'thermal_stabilization'
    return_type = 'object'

class scale_factor(Real, AllowedValuesMixin):
    """
    'scale_factor' child.
    """
    _version = '222'
    fluent_name = 'scale-factor'
    _python_name = 'scale_factor'
    return_type = 'object'

class stab_method(String, AllowedValuesMixin):
    """
    'stab_method' child.
    """
    _version = '222'
    fluent_name = 'stab-method'
    _python_name = 'stab_method'
    return_type = 'object'

class fensapice_ice_icing_mode(Integer, AllowedValuesMixin):
    """
    'fensapice_ice_icing_mode' child.
    """
    _version = '222'
    fluent_name = 'fensapice-ice-icing-mode'
    _python_name = 'fensapice_ice_icing_mode'
    return_type = 'object'

class fensapice_ice_hflux(Boolean, AllowedValuesMixin):
    """
    'fensapice_ice_hflux' child.
    """
    _version = '222'
    fluent_name = 'fensapice-ice-hflux?'
    _python_name = 'fensapice_ice_hflux'
    return_type = 'object'

class fensapice_ice_hflux_1(Real, AllowedValuesMixin):
    """
    'fensapice_ice_hflux' child.
    """
    _version = '222'
    fluent_name = 'fensapice-ice-hflux'
    _python_name = 'fensapice_ice_hflux'
    return_type = 'object'

class fensapice_drop_vwet(Boolean, AllowedValuesMixin):
    """
    'fensapice_drop_vwet' child.
    """
    _version = '222'
    fluent_name = 'fensapice-drop-vwet?'
    _python_name = 'fensapice_drop_vwet'
    return_type = 'object'

class phase_24_child(Group):
    """
    'child_object_type' of phase.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'phase_child'
    child_names = ['geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'd', 'q_dot', 'material', 'thermal_bc', 't', 'q', 'h', 'tinf', 'planar_conduction', 'shell_conduction', 'thin_wall', 'motion_bc', 'shear_bc', 'rough_bc', 'moving', 'relative', 'rotating', 'vmag', 'component_of_wall_translation', 'components', 'x_velocity', 'y_velocity', 'z_velocity', 'velocity_components', 'in_emiss', 'ex_emiss', 'trad', 'int_rad', 'trad_internal', 'area_enhancement_factor', 'rough_option', 'rough_nasa', 'rough_shin_et_al', 'rough_data', 'roughness_height', 'roughness_const', 'roughness_height_cp', 'roughness_const_cp', 'roughness_const_nasa', 'roughness_const_shin', 'roughness_const_data', 'variable_roughness', 'free_stream_velocity', 'free_stream_temp', 'characteristic_length', 'free_stream_temp_cp', 'characteristic_length_cp', 'liquid_content', 'liquid_content_cp', 'droplet_diameter', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_norm_coeff', 'dpm_bc_tang_coeff', 'dpm_bc_frictn_coeff', 'dpm_bc_udf', 'dpm_film_splash_nsamp', 'dpm_crit_temp_option', 'dpm_critical_temp_factor', 'dpm_calibratable_temp', 'dpm_impingement_splashing_model', 'dpm_upper_deposition_limit_offset', 'dpm_deposition_delta_t', 'dpm_laplace_number_constant', 'dpm_partial_evaporation_ratio', 'ra_roughness', 'rz_roughness', 'rq_roughness', 'rsm_roughness', 'dpm_bc_erosion_generic', 'dpm_bc_erosion', 'dpm_bc_erosion_c', 'dpm_bc_erosion_n', 'dpm_bc_erosion_finnie', 'dpm_bc_erosion_finnie_k', 'dpm_bc_erosion_finnie_vel_exp', 'dpm_bc_erosion_finnie_max_erosion_angle', 'dpm_bc_erosion_mclaury', 'dpm_bc_erosion_mclaury_a', 'dpm_bc_erosion_mclaury_vel_exp', 'dpm_bc_erosion_mclaury_transition_angle', 'dpm_bc_erosion_mclaury_b', 'dpm_bc_erosion_mclaury_c', 'dpm_bc_erosion_mclaury_w', 'dpm_bc_erosion_mclaury_x', 'dpm_bc_erosion_mclaury_y', 'dpm_bc_erosion_oka', 'dpm_bc_erosion_oka_e90', 'dpm_bc_erosion_oka_hv', 'dpm_bc_erosion_oka_n1', 'dpm_bc_erosion_oka_n2', 'dpm_bc_erosion_oka_k2', 'dpm_bc_erosion_oka_k3', 'dpm_bc_erosion_oka_dref', 'dpm_bc_erosion_oka_vref', 'dpm_bc_erosion_dnv', 'dpm_bc_erosion_dnv_k', 'dpm_bc_erosion_dnv_n', 'dpm_bc_erosion_dnv_ductile', 'dpm_bc_erosion_shear', 'dpm_bc_erosion_shear_v', 'dpm_bc_erosion_shear_c', 'dpm_bc_erosion_shear_packing_limit', 'dpm_bc_erosion_shielding', 'dpm_wall_heat_exchange', 'dpm_film_condensation', 'dpm_film_bl_model', 'dpm_particle_stripping', 'dpm_critical_shear_stress', 'dpm_film_separation_model', 'dpm_critical_we_number', 'dpm_film_separation_angle', 'dpm_allow_lwf_to_vof', 'dpm_allow_vof_to_lwf', 'dpm_initialize_lwf', 'dpm_initial_height', 'film_velocity', 'dpm_initial_temperature', 'dpm_initial_injection', 'film_parcel_surface_area_density', 'minimum_number_of_parcels_per_face', 'band_in_emiss', 'radiation_bc', 'mc_bsource_p', 'mc_poldfun_p', 'polar_func_type', 'mc_polar_expr', 'polar_pair_list', 'pold_pair_list_rad', 'component_of_radiation_direction', 'coll_dtheta', 'coll_dphi', 'band_q_irrad', 'band_q_irrad_diffuse', 'band_diffuse_frac', 'radiating_s2s_surface', 'critical_zone', 'fpsc', 'parallel_collimated_beam', 'solar_fluxes', 'solar_direction', 'solar_irradiation', 'v_transmissivity', 'ir_transmissivity', 'v_opq_absorbtivity', 'ir_opq_absorbtivity', 'v_st_absorbtivity', 'ir_st_absorbtivity', 'd_st_absorbtivity', 'd_transmissivity', 'fsi_interface', 'react', 'partially_catalytic', 'partially_catalytic_material', 'partially_catalytic_recombination_coefficient_o', 'partially_catalytic_recombination_coefficient_n', 'partially_catalytic_recombination_model', 'species_spec', 'mf', 'elec_potential_type', 'potential_value', 'elec_potential_jump', 'elec_potential_resistance', 'dual_potential_type', 'dual_potential_value', 'echem_reaction', 'elec_potential_mechs', 'faradaic_heat', 'li_ion_type', 'li_ion_value', 'x_displacement_type', 'x_displacement_value', 'y_displacement_type', 'y_displacement_value', 'z_displacement_type', 'z_displacement_value', 'per_dispx', 'per_dispy', 'per_dispz', 'per_imagx', 'per_imagy', 'per_imagz', 'freq', 'amp', 'nodal_diam', 'pass_number', 'fwd', 'aero', 'cmplx', 'norm', 'method', 'uds_bc', 'uds', 'gtemp_bc', 'g_temperature', 'g_qflux', 'wall_restitution_coeff', 'omega', 'origin_position_of_rotation_axis', 'direction_component_of_rotation_axis', 'adhesion_angle', 'specified_shear', 'shear_y', 'shear_z', 'shear_stress_components', 'fslip', 'eslip', 'surf_tens_grad', 'contact_resistance', 'reaction_mechs', 'surf_washcoat_factor', 'ablation_select_model', 'ablation_vielle_a', 'ablation_vielle_n', 'ablation_surfacerxn_density', 'ablation_flux', 'ablation_species_mf', 'specular_coeff', 'mom_accom_coef', 'therm_accom_coef', 'eve_accom_coef', 'film_wall', 'film_wall_bc', 'film_height', 'flux_momentum_components', 'film_relative_vel', 'film_bc_imp_press', 'film_temperature', 'film_scalar', 'film_source', 'film_h_src', 'film_u_src', 'film_v_src', 'film_w_src', 'momentum_source_components', 'film_t_src', 'film_s_src', 'film_phase_change', 'film_phase_change_model', 'film_cond_const', 'film_vapo_const', 'film_cond_rate', 'film_vapo_rate', 'film_momentum_coupling', 'film_splash_wall', 'film_boundary_separation', 'film_impinge_model', 'film_splash_nparc', 'film_crit_temp_factor', 'film_roughness_ra', 'film_roughness_rz', 'film_upper_deposition_limit_offset', 'film_deposition_delta_t', 'film_laplace_number_constant', 'film_partial_evap_ratio', 'film_contact_angle', 'film_contact_angle_mean', 'film_contact_angle_rstd', 'film_contact_angle_beta', 'film_vof_coupling_high', 'film_vof_trans_high', 'film_vof_trans_high_relax', 'film_vof_coupling_low', 'film_vof_trans_low', 'film_vof_trans_low_relax', 'caf', 'thermal_stabilization', 'scale_factor', 'stab_method', 'fensapice_ice_icing_mode', 'fensapice_ice_hflux', 'fensapice_ice_hflux_1', 'fensapice_drop_vwet']
    _child_classes = dict(
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        d=d,
        q_dot=q_dot,
        material=material,
        thermal_bc=thermal_bc,
        t=t,
        q=q,
        h=h,
        tinf=tinf_1,
        planar_conduction=planar_conduction,
        shell_conduction=shell_conduction,
        thin_wall=thin_wall,
        motion_bc=motion_bc,
        shear_bc=shear_bc,
        rough_bc=rough_bc,
        moving=moving,
        relative=relative,
        rotating=rotating,
        vmag=vmag,
        component_of_wall_translation=component_of_wall_translation,
        components=components_1,
        x_velocity=x_velocity,
        y_velocity=y_velocity,
        z_velocity=z_velocity,
        velocity_components=velocity_components,
        in_emiss=in_emiss,
        ex_emiss=ex_emiss,
        trad=trad,
        int_rad=int_rad,
        trad_internal=trad_internal,
        area_enhancement_factor=area_enhancement_factor,
        rough_option=rough_option,
        rough_nasa=rough_nasa,
        rough_shin_et_al=rough_shin_et_al,
        rough_data=rough_data,
        roughness_height=roughness_height,
        roughness_const=roughness_const,
        roughness_height_cp=roughness_height_cp,
        roughness_const_cp=roughness_const_cp,
        roughness_const_nasa=roughness_const_nasa,
        roughness_const_shin=roughness_const_shin,
        roughness_const_data=roughness_const_data,
        variable_roughness=variable_roughness,
        free_stream_velocity=free_stream_velocity,
        free_stream_temp=free_stream_temp,
        characteristic_length=characteristic_length,
        free_stream_temp_cp=free_stream_temp_cp,
        characteristic_length_cp=characteristic_length_cp,
        liquid_content=liquid_content,
        liquid_content_cp=liquid_content_cp,
        droplet_diameter=droplet_diameter,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_norm_coeff=dpm_bc_norm_coeff,
        dpm_bc_tang_coeff=dpm_bc_tang_coeff,
        dpm_bc_frictn_coeff=dpm_bc_frictn_coeff,
        dpm_bc_udf=dpm_bc_udf,
        dpm_film_splash_nsamp=dpm_film_splash_nsamp,
        dpm_crit_temp_option=dpm_crit_temp_option,
        dpm_critical_temp_factor=dpm_critical_temp_factor,
        dpm_calibratable_temp=dpm_calibratable_temp,
        dpm_impingement_splashing_model=dpm_impingement_splashing_model,
        dpm_upper_deposition_limit_offset=dpm_upper_deposition_limit_offset,
        dpm_deposition_delta_t=dpm_deposition_delta_t,
        dpm_laplace_number_constant=dpm_laplace_number_constant,
        dpm_partial_evaporation_ratio=dpm_partial_evaporation_ratio,
        ra_roughness=ra_roughness,
        rz_roughness=rz_roughness,
        rq_roughness=rq_roughness,
        rsm_roughness=rsm_roughness,
        dpm_bc_erosion_generic=dpm_bc_erosion_generic,
        dpm_bc_erosion=dpm_bc_erosion,
        dpm_bc_erosion_c=dpm_bc_erosion_c,
        dpm_bc_erosion_n=dpm_bc_erosion_n,
        dpm_bc_erosion_finnie=dpm_bc_erosion_finnie,
        dpm_bc_erosion_finnie_k=dpm_bc_erosion_finnie_k,
        dpm_bc_erosion_finnie_vel_exp=dpm_bc_erosion_finnie_vel_exp,
        dpm_bc_erosion_finnie_max_erosion_angle=dpm_bc_erosion_finnie_max_erosion_angle,
        dpm_bc_erosion_mclaury=dpm_bc_erosion_mclaury,
        dpm_bc_erosion_mclaury_a=dpm_bc_erosion_mclaury_a,
        dpm_bc_erosion_mclaury_vel_exp=dpm_bc_erosion_mclaury_vel_exp,
        dpm_bc_erosion_mclaury_transition_angle=dpm_bc_erosion_mclaury_transition_angle,
        dpm_bc_erosion_mclaury_b=dpm_bc_erosion_mclaury_b,
        dpm_bc_erosion_mclaury_c=dpm_bc_erosion_mclaury_c,
        dpm_bc_erosion_mclaury_w=dpm_bc_erosion_mclaury_w,
        dpm_bc_erosion_mclaury_x=dpm_bc_erosion_mclaury_x,
        dpm_bc_erosion_mclaury_y=dpm_bc_erosion_mclaury_y,
        dpm_bc_erosion_oka=dpm_bc_erosion_oka,
        dpm_bc_erosion_oka_e90=dpm_bc_erosion_oka_e90,
        dpm_bc_erosion_oka_hv=dpm_bc_erosion_oka_hv,
        dpm_bc_erosion_oka_n1=dpm_bc_erosion_oka_n1,
        dpm_bc_erosion_oka_n2=dpm_bc_erosion_oka_n2,
        dpm_bc_erosion_oka_k2=dpm_bc_erosion_oka_k2,
        dpm_bc_erosion_oka_k3=dpm_bc_erosion_oka_k3,
        dpm_bc_erosion_oka_dref=dpm_bc_erosion_oka_dref,
        dpm_bc_erosion_oka_vref=dpm_bc_erosion_oka_vref,
        dpm_bc_erosion_dnv=dpm_bc_erosion_dnv,
        dpm_bc_erosion_dnv_k=dpm_bc_erosion_dnv_k,
        dpm_bc_erosion_dnv_n=dpm_bc_erosion_dnv_n,
        dpm_bc_erosion_dnv_ductile=dpm_bc_erosion_dnv_ductile,
        dpm_bc_erosion_shear=dpm_bc_erosion_shear,
        dpm_bc_erosion_shear_v=dpm_bc_erosion_shear_v,
        dpm_bc_erosion_shear_c=dpm_bc_erosion_shear_c,
        dpm_bc_erosion_shear_packing_limit=dpm_bc_erosion_shear_packing_limit,
        dpm_bc_erosion_shielding=dpm_bc_erosion_shielding,
        dpm_wall_heat_exchange=dpm_wall_heat_exchange,
        dpm_film_condensation=dpm_film_condensation,
        dpm_film_bl_model=dpm_film_bl_model,
        dpm_particle_stripping=dpm_particle_stripping,
        dpm_critical_shear_stress=dpm_critical_shear_stress,
        dpm_film_separation_model=dpm_film_separation_model,
        dpm_critical_we_number=dpm_critical_we_number,
        dpm_film_separation_angle=dpm_film_separation_angle,
        dpm_allow_lwf_to_vof=dpm_allow_lwf_to_vof,
        dpm_allow_vof_to_lwf=dpm_allow_vof_to_lwf,
        dpm_initialize_lwf=dpm_initialize_lwf,
        dpm_initial_height=dpm_initial_height,
        film_velocity=film_velocity,
        dpm_initial_temperature=dpm_initial_temperature,
        dpm_initial_injection=dpm_initial_injection,
        film_parcel_surface_area_density=film_parcel_surface_area_density,
        minimum_number_of_parcels_per_face=minimum_number_of_parcels_per_face,
        band_in_emiss=band_in_emiss,
        radiation_bc=radiation_bc,
        mc_bsource_p=mc_bsource_p,
        mc_poldfun_p=mc_poldfun_p,
        polar_func_type=polar_func_type,
        mc_polar_expr=mc_polar_expr,
        polar_pair_list=polar_pair_list,
        pold_pair_list_rad=pold_pair_list_rad,
        component_of_radiation_direction=component_of_radiation_direction,
        coll_dtheta=coll_dtheta,
        coll_dphi=coll_dphi,
        band_q_irrad=band_q_irrad,
        band_q_irrad_diffuse=band_q_irrad_diffuse,
        band_diffuse_frac=band_diffuse_frac,
        radiating_s2s_surface=radiating_s2s_surface,
        critical_zone=critical_zone,
        fpsc=fpsc,
        parallel_collimated_beam=parallel_collimated_beam,
        solar_fluxes=solar_fluxes,
        solar_direction=solar_direction,
        solar_irradiation=solar_irradiation,
        v_transmissivity=v_transmissivity,
        ir_transmissivity=ir_transmissivity,
        v_opq_absorbtivity=v_opq_absorbtivity,
        ir_opq_absorbtivity=ir_opq_absorbtivity,
        v_st_absorbtivity=v_st_absorbtivity,
        ir_st_absorbtivity=ir_st_absorbtivity,
        d_st_absorbtivity=d_st_absorbtivity,
        d_transmissivity=d_transmissivity,
        fsi_interface=fsi_interface,
        react=react,
        partially_catalytic=partially_catalytic,
        partially_catalytic_material=partially_catalytic_material,
        partially_catalytic_recombination_coefficient_o=partially_catalytic_recombination_coefficient_o,
        partially_catalytic_recombination_coefficient_n=partially_catalytic_recombination_coefficient_n,
        partially_catalytic_recombination_model=partially_catalytic_recombination_model,
        species_spec=species_spec,
        mf=mf,
        elec_potential_type=elec_potential_type,
        potential_value=potential_value,
        elec_potential_jump=elec_potential_jump,
        elec_potential_resistance=elec_potential_resistance,
        dual_potential_type=dual_potential_type,
        dual_potential_value=dual_potential_value,
        echem_reaction=echem_reaction,
        elec_potential_mechs=elec_potential_mechs,
        faradaic_heat=faradaic_heat,
        li_ion_type=li_ion_type,
        li_ion_value=li_ion_value,
        x_displacement_type=x_displacement_type,
        x_displacement_value=x_displacement_value,
        y_displacement_type=y_displacement_type,
        y_displacement_value=y_displacement_value,
        z_displacement_type=z_displacement_type,
        z_displacement_value=z_displacement_value,
        per_dispx=per_dispx,
        per_dispy=per_dispy,
        per_dispz=per_dispz,
        per_imagx=per_imagx,
        per_imagy=per_imagy,
        per_imagz=per_imagz,
        freq=freq,
        amp=amp,
        nodal_diam=nodal_diam,
        pass_number=pass_number,
        fwd=fwd,
        aero=aero,
        cmplx=cmplx,
        norm=norm,
        method=method_1,
        uds_bc=uds_bc,
        uds=uds,
        gtemp_bc=gtemp_bc,
        g_temperature=g_temperature,
        g_qflux=g_qflux,
        wall_restitution_coeff=wall_restitution_coeff,
        omega=omega,
        origin_position_of_rotation_axis=origin_position_of_rotation_axis,
        direction_component_of_rotation_axis=direction_component_of_rotation_axis,
        adhesion_angle=adhesion_angle,
        specified_shear=specified_shear,
        shear_y=shear_y,
        shear_z=shear_z,
        shear_stress_components=shear_stress_components,
        fslip=fslip,
        eslip=eslip,
        surf_tens_grad=surf_tens_grad,
        contact_resistance=contact_resistance,
        reaction_mechs=reaction_mechs_1,
        surf_washcoat_factor=surf_washcoat_factor,
        ablation_select_model=ablation_select_model,
        ablation_vielle_a=ablation_vielle_a,
        ablation_vielle_n=ablation_vielle_n,
        ablation_surfacerxn_density=ablation_surfacerxn_density,
        ablation_flux=ablation_flux,
        ablation_species_mf=ablation_species_mf,
        specular_coeff=specular_coeff,
        mom_accom_coef=mom_accom_coef,
        therm_accom_coef=therm_accom_coef,
        eve_accom_coef=eve_accom_coef,
        film_wall=film_wall,
        film_wall_bc=film_wall_bc,
        film_height=film_height,
        flux_momentum_components=flux_momentum_components,
        film_relative_vel=film_relative_vel,
        film_bc_imp_press=film_bc_imp_press,
        film_temperature=film_temperature,
        film_scalar=film_scalar,
        film_source=film_source,
        film_h_src=film_h_src,
        film_u_src=film_u_src,
        film_v_src=film_v_src,
        film_w_src=film_w_src,
        momentum_source_components=momentum_source_components,
        film_t_src=film_t_src,
        film_s_src=film_s_src,
        film_phase_change=film_phase_change,
        film_phase_change_model=film_phase_change_model,
        film_cond_const=film_cond_const,
        film_vapo_const=film_vapo_const,
        film_cond_rate=film_cond_rate,
        film_vapo_rate=film_vapo_rate,
        film_momentum_coupling=film_momentum_coupling,
        film_splash_wall=film_splash_wall,
        film_boundary_separation=film_boundary_separation,
        film_impinge_model=film_impinge_model,
        film_splash_nparc=film_splash_nparc,
        film_crit_temp_factor=film_crit_temp_factor,
        film_roughness_ra=film_roughness_ra,
        film_roughness_rz=film_roughness_rz,
        film_upper_deposition_limit_offset=film_upper_deposition_limit_offset,
        film_deposition_delta_t=film_deposition_delta_t,
        film_laplace_number_constant=film_laplace_number_constant,
        film_partial_evap_ratio=film_partial_evap_ratio,
        film_contact_angle=film_contact_angle,
        film_contact_angle_mean=film_contact_angle_mean,
        film_contact_angle_rstd=film_contact_angle_rstd,
        film_contact_angle_beta=film_contact_angle_beta,
        film_vof_coupling_high=film_vof_coupling_high,
        film_vof_trans_high=film_vof_trans_high,
        film_vof_trans_high_relax=film_vof_trans_high_relax,
        film_vof_coupling_low=film_vof_coupling_low,
        film_vof_trans_low=film_vof_trans_low,
        film_vof_trans_low_relax=film_vof_trans_low_relax,
        caf=caf,
        thermal_stabilization=thermal_stabilization,
        scale_factor=scale_factor,
        stab_method=stab_method,
        fensapice_ice_icing_mode=fensapice_ice_icing_mode,
        fensapice_ice_hflux=fensapice_ice_hflux,
        fensapice_ice_hflux_1=fensapice_ice_hflux_1,
        fensapice_drop_vwet=fensapice_drop_vwet,
    )
    return_type = 'object'

class phase_24(NamedObject[phase_24_child], CreatableNamedObjectMixinOld[phase_24_child]):
    """
    'phase' child.
    """
    _version = '222'
    fluent_name = 'phase'
    _python_name = 'phase'
    child_object_type = phase_24_child
    return_type = 'object'

class wall_child(Group):
    """
    'child_object_type' of wall.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'wall_child'
    child_names = ['phase', 'geom_disable', 'geom_dir_spec', 'geom_dir_x', 'geom_dir_y', 'geom_dir_z', 'geom_levels', 'geom_bgthread', 'd', 'q_dot', 'material', 'thermal_bc', 't', 'q', 'h', 'tinf', 'planar_conduction', 'shell_conduction', 'thin_wall', 'motion_bc', 'shear_bc', 'rough_bc', 'moving', 'relative', 'rotating', 'vmag', 'component_of_wall_translation', 'components', 'x_velocity', 'y_velocity', 'z_velocity', 'velocity_components', 'in_emiss', 'ex_emiss', 'trad', 'int_rad', 'trad_internal', 'area_enhancement_factor', 'rough_option', 'rough_nasa', 'rough_shin_et_al', 'rough_data', 'roughness_height', 'roughness_const', 'roughness_height_cp', 'roughness_const_cp', 'roughness_const_nasa', 'roughness_const_shin', 'roughness_const_data', 'variable_roughness', 'free_stream_velocity', 'free_stream_temp', 'characteristic_length', 'free_stream_temp_cp', 'characteristic_length_cp', 'liquid_content', 'liquid_content_cp', 'droplet_diameter', 'dpm_bc_type', 'dpm_bc_collision_partner', 'reinj_inj', 'dpm_bc_norm_coeff', 'dpm_bc_tang_coeff', 'dpm_bc_frictn_coeff', 'dpm_bc_udf', 'dpm_film_splash_nsamp', 'dpm_crit_temp_option', 'dpm_critical_temp_factor', 'dpm_calibratable_temp', 'dpm_impingement_splashing_model', 'dpm_upper_deposition_limit_offset', 'dpm_deposition_delta_t', 'dpm_laplace_number_constant', 'dpm_partial_evaporation_ratio', 'ra_roughness', 'rz_roughness', 'rq_roughness', 'rsm_roughness', 'dpm_bc_erosion_generic', 'dpm_bc_erosion', 'dpm_bc_erosion_c', 'dpm_bc_erosion_n', 'dpm_bc_erosion_finnie', 'dpm_bc_erosion_finnie_k', 'dpm_bc_erosion_finnie_vel_exp', 'dpm_bc_erosion_finnie_max_erosion_angle', 'dpm_bc_erosion_mclaury', 'dpm_bc_erosion_mclaury_a', 'dpm_bc_erosion_mclaury_vel_exp', 'dpm_bc_erosion_mclaury_transition_angle', 'dpm_bc_erosion_mclaury_b', 'dpm_bc_erosion_mclaury_c', 'dpm_bc_erosion_mclaury_w', 'dpm_bc_erosion_mclaury_x', 'dpm_bc_erosion_mclaury_y', 'dpm_bc_erosion_oka', 'dpm_bc_erosion_oka_e90', 'dpm_bc_erosion_oka_hv', 'dpm_bc_erosion_oka_n1', 'dpm_bc_erosion_oka_n2', 'dpm_bc_erosion_oka_k2', 'dpm_bc_erosion_oka_k3', 'dpm_bc_erosion_oka_dref', 'dpm_bc_erosion_oka_vref', 'dpm_bc_erosion_dnv', 'dpm_bc_erosion_dnv_k', 'dpm_bc_erosion_dnv_n', 'dpm_bc_erosion_dnv_ductile', 'dpm_bc_erosion_shear', 'dpm_bc_erosion_shear_v', 'dpm_bc_erosion_shear_c', 'dpm_bc_erosion_shear_packing_limit', 'dpm_bc_erosion_shielding', 'dpm_wall_heat_exchange', 'dpm_film_condensation', 'dpm_film_bl_model', 'dpm_particle_stripping', 'dpm_critical_shear_stress', 'dpm_film_separation_model', 'dpm_critical_we_number', 'dpm_film_separation_angle', 'dpm_allow_lwf_to_vof', 'dpm_allow_vof_to_lwf', 'dpm_initialize_lwf', 'dpm_initial_height', 'film_velocity', 'dpm_initial_temperature', 'dpm_initial_injection', 'film_parcel_surface_area_density', 'minimum_number_of_parcels_per_face', 'band_in_emiss', 'radiation_bc', 'mc_bsource_p', 'mc_poldfun_p', 'polar_func_type', 'mc_polar_expr', 'polar_pair_list', 'pold_pair_list_rad', 'component_of_radiation_direction', 'coll_dtheta', 'coll_dphi', 'band_q_irrad', 'band_q_irrad_diffuse', 'band_diffuse_frac', 'radiating_s2s_surface', 'critical_zone', 'fpsc', 'parallel_collimated_beam', 'solar_fluxes', 'solar_direction', 'solar_irradiation', 'v_transmissivity', 'ir_transmissivity', 'v_opq_absorbtivity', 'ir_opq_absorbtivity', 'v_st_absorbtivity', 'ir_st_absorbtivity', 'd_st_absorbtivity', 'd_transmissivity', 'fsi_interface', 'react', 'partially_catalytic', 'partially_catalytic_material', 'partially_catalytic_recombination_coefficient_o', 'partially_catalytic_recombination_coefficient_n', 'partially_catalytic_recombination_model', 'species_spec', 'mf', 'elec_potential_type', 'potential_value', 'elec_potential_jump', 'elec_potential_resistance', 'dual_potential_type', 'dual_potential_value', 'echem_reaction', 'elec_potential_mechs', 'faradaic_heat', 'li_ion_type', 'li_ion_value', 'x_displacement_type', 'x_displacement_value', 'y_displacement_type', 'y_displacement_value', 'z_displacement_type', 'z_displacement_value', 'per_dispx', 'per_dispy', 'per_dispz', 'per_imagx', 'per_imagy', 'per_imagz', 'freq', 'amp', 'nodal_diam', 'pass_number', 'fwd', 'aero', 'cmplx', 'norm', 'method', 'uds_bc', 'uds', 'gtemp_bc', 'g_temperature', 'g_qflux', 'wall_restitution_coeff', 'omega', 'origin_position_of_rotation_axis', 'direction_component_of_rotation_axis', 'adhesion_angle', 'specified_shear', 'shear_y', 'shear_z', 'shear_stress_components', 'fslip', 'eslip', 'surf_tens_grad', 'contact_resistance', 'reaction_mechs', 'surf_washcoat_factor', 'ablation_select_model', 'ablation_vielle_a', 'ablation_vielle_n', 'ablation_surfacerxn_density', 'ablation_flux', 'ablation_species_mf', 'specular_coeff', 'mom_accom_coef', 'therm_accom_coef', 'eve_accom_coef', 'film_wall', 'film_wall_bc', 'film_height', 'flux_momentum_components', 'film_relative_vel', 'film_bc_imp_press', 'film_temperature', 'film_scalar', 'film_source', 'film_h_src', 'film_u_src', 'film_v_src', 'film_w_src', 'momentum_source_components', 'film_t_src', 'film_s_src', 'film_phase_change', 'film_phase_change_model', 'film_cond_const', 'film_vapo_const', 'film_cond_rate', 'film_vapo_rate', 'film_momentum_coupling', 'film_splash_wall', 'film_boundary_separation', 'film_impinge_model', 'film_splash_nparc', 'film_crit_temp_factor', 'film_roughness_ra', 'film_roughness_rz', 'film_upper_deposition_limit_offset', 'film_deposition_delta_t', 'film_laplace_number_constant', 'film_partial_evap_ratio', 'film_contact_angle', 'film_contact_angle_mean', 'film_contact_angle_rstd', 'film_contact_angle_beta', 'film_vof_coupling_high', 'film_vof_trans_high', 'film_vof_trans_high_relax', 'film_vof_coupling_low', 'film_vof_trans_low', 'film_vof_trans_low_relax', 'caf', 'thermal_stabilization', 'scale_factor', 'stab_method', 'fensapice_ice_icing_mode', 'fensapice_ice_hflux', 'fensapice_ice_hflux_1', 'fensapice_drop_vwet']
    _child_classes = dict(
        phase=phase_24,
        geom_disable=geom_disable,
        geom_dir_spec=geom_dir_spec,
        geom_dir_x=geom_dir_x,
        geom_dir_y=geom_dir_y,
        geom_dir_z=geom_dir_z,
        geom_levels=geom_levels,
        geom_bgthread=geom_bgthread,
        d=d,
        q_dot=q_dot,
        material=material,
        thermal_bc=thermal_bc,
        t=t,
        q=q,
        h=h,
        tinf=tinf_1,
        planar_conduction=planar_conduction,
        shell_conduction=shell_conduction,
        thin_wall=thin_wall,
        motion_bc=motion_bc,
        shear_bc=shear_bc,
        rough_bc=rough_bc,
        moving=moving,
        relative=relative,
        rotating=rotating,
        vmag=vmag,
        component_of_wall_translation=component_of_wall_translation,
        components=components_1,
        x_velocity=x_velocity,
        y_velocity=y_velocity,
        z_velocity=z_velocity,
        velocity_components=velocity_components,
        in_emiss=in_emiss,
        ex_emiss=ex_emiss,
        trad=trad,
        int_rad=int_rad,
        trad_internal=trad_internal,
        area_enhancement_factor=area_enhancement_factor,
        rough_option=rough_option,
        rough_nasa=rough_nasa,
        rough_shin_et_al=rough_shin_et_al,
        rough_data=rough_data,
        roughness_height=roughness_height,
        roughness_const=roughness_const,
        roughness_height_cp=roughness_height_cp,
        roughness_const_cp=roughness_const_cp,
        roughness_const_nasa=roughness_const_nasa,
        roughness_const_shin=roughness_const_shin,
        roughness_const_data=roughness_const_data,
        variable_roughness=variable_roughness,
        free_stream_velocity=free_stream_velocity,
        free_stream_temp=free_stream_temp,
        characteristic_length=characteristic_length,
        free_stream_temp_cp=free_stream_temp_cp,
        characteristic_length_cp=characteristic_length_cp,
        liquid_content=liquid_content,
        liquid_content_cp=liquid_content_cp,
        droplet_diameter=droplet_diameter,
        dpm_bc_type=dpm_bc_type,
        dpm_bc_collision_partner=dpm_bc_collision_partner,
        reinj_inj=reinj_inj,
        dpm_bc_norm_coeff=dpm_bc_norm_coeff,
        dpm_bc_tang_coeff=dpm_bc_tang_coeff,
        dpm_bc_frictn_coeff=dpm_bc_frictn_coeff,
        dpm_bc_udf=dpm_bc_udf,
        dpm_film_splash_nsamp=dpm_film_splash_nsamp,
        dpm_crit_temp_option=dpm_crit_temp_option,
        dpm_critical_temp_factor=dpm_critical_temp_factor,
        dpm_calibratable_temp=dpm_calibratable_temp,
        dpm_impingement_splashing_model=dpm_impingement_splashing_model,
        dpm_upper_deposition_limit_offset=dpm_upper_deposition_limit_offset,
        dpm_deposition_delta_t=dpm_deposition_delta_t,
        dpm_laplace_number_constant=dpm_laplace_number_constant,
        dpm_partial_evaporation_ratio=dpm_partial_evaporation_ratio,
        ra_roughness=ra_roughness,
        rz_roughness=rz_roughness,
        rq_roughness=rq_roughness,
        rsm_roughness=rsm_roughness,
        dpm_bc_erosion_generic=dpm_bc_erosion_generic,
        dpm_bc_erosion=dpm_bc_erosion,
        dpm_bc_erosion_c=dpm_bc_erosion_c,
        dpm_bc_erosion_n=dpm_bc_erosion_n,
        dpm_bc_erosion_finnie=dpm_bc_erosion_finnie,
        dpm_bc_erosion_finnie_k=dpm_bc_erosion_finnie_k,
        dpm_bc_erosion_finnie_vel_exp=dpm_bc_erosion_finnie_vel_exp,
        dpm_bc_erosion_finnie_max_erosion_angle=dpm_bc_erosion_finnie_max_erosion_angle,
        dpm_bc_erosion_mclaury=dpm_bc_erosion_mclaury,
        dpm_bc_erosion_mclaury_a=dpm_bc_erosion_mclaury_a,
        dpm_bc_erosion_mclaury_vel_exp=dpm_bc_erosion_mclaury_vel_exp,
        dpm_bc_erosion_mclaury_transition_angle=dpm_bc_erosion_mclaury_transition_angle,
        dpm_bc_erosion_mclaury_b=dpm_bc_erosion_mclaury_b,
        dpm_bc_erosion_mclaury_c=dpm_bc_erosion_mclaury_c,
        dpm_bc_erosion_mclaury_w=dpm_bc_erosion_mclaury_w,
        dpm_bc_erosion_mclaury_x=dpm_bc_erosion_mclaury_x,
        dpm_bc_erosion_mclaury_y=dpm_bc_erosion_mclaury_y,
        dpm_bc_erosion_oka=dpm_bc_erosion_oka,
        dpm_bc_erosion_oka_e90=dpm_bc_erosion_oka_e90,
        dpm_bc_erosion_oka_hv=dpm_bc_erosion_oka_hv,
        dpm_bc_erosion_oka_n1=dpm_bc_erosion_oka_n1,
        dpm_bc_erosion_oka_n2=dpm_bc_erosion_oka_n2,
        dpm_bc_erosion_oka_k2=dpm_bc_erosion_oka_k2,
        dpm_bc_erosion_oka_k3=dpm_bc_erosion_oka_k3,
        dpm_bc_erosion_oka_dref=dpm_bc_erosion_oka_dref,
        dpm_bc_erosion_oka_vref=dpm_bc_erosion_oka_vref,
        dpm_bc_erosion_dnv=dpm_bc_erosion_dnv,
        dpm_bc_erosion_dnv_k=dpm_bc_erosion_dnv_k,
        dpm_bc_erosion_dnv_n=dpm_bc_erosion_dnv_n,
        dpm_bc_erosion_dnv_ductile=dpm_bc_erosion_dnv_ductile,
        dpm_bc_erosion_shear=dpm_bc_erosion_shear,
        dpm_bc_erosion_shear_v=dpm_bc_erosion_shear_v,
        dpm_bc_erosion_shear_c=dpm_bc_erosion_shear_c,
        dpm_bc_erosion_shear_packing_limit=dpm_bc_erosion_shear_packing_limit,
        dpm_bc_erosion_shielding=dpm_bc_erosion_shielding,
        dpm_wall_heat_exchange=dpm_wall_heat_exchange,
        dpm_film_condensation=dpm_film_condensation,
        dpm_film_bl_model=dpm_film_bl_model,
        dpm_particle_stripping=dpm_particle_stripping,
        dpm_critical_shear_stress=dpm_critical_shear_stress,
        dpm_film_separation_model=dpm_film_separation_model,
        dpm_critical_we_number=dpm_critical_we_number,
        dpm_film_separation_angle=dpm_film_separation_angle,
        dpm_allow_lwf_to_vof=dpm_allow_lwf_to_vof,
        dpm_allow_vof_to_lwf=dpm_allow_vof_to_lwf,
        dpm_initialize_lwf=dpm_initialize_lwf,
        dpm_initial_height=dpm_initial_height,
        film_velocity=film_velocity,
        dpm_initial_temperature=dpm_initial_temperature,
        dpm_initial_injection=dpm_initial_injection,
        film_parcel_surface_area_density=film_parcel_surface_area_density,
        minimum_number_of_parcels_per_face=minimum_number_of_parcels_per_face,
        band_in_emiss=band_in_emiss,
        radiation_bc=radiation_bc,
        mc_bsource_p=mc_bsource_p,
        mc_poldfun_p=mc_poldfun_p,
        polar_func_type=polar_func_type,
        mc_polar_expr=mc_polar_expr,
        polar_pair_list=polar_pair_list,
        pold_pair_list_rad=pold_pair_list_rad,
        component_of_radiation_direction=component_of_radiation_direction,
        coll_dtheta=coll_dtheta,
        coll_dphi=coll_dphi,
        band_q_irrad=band_q_irrad,
        band_q_irrad_diffuse=band_q_irrad_diffuse,
        band_diffuse_frac=band_diffuse_frac,
        radiating_s2s_surface=radiating_s2s_surface,
        critical_zone=critical_zone,
        fpsc=fpsc,
        parallel_collimated_beam=parallel_collimated_beam,
        solar_fluxes=solar_fluxes,
        solar_direction=solar_direction,
        solar_irradiation=solar_irradiation,
        v_transmissivity=v_transmissivity,
        ir_transmissivity=ir_transmissivity,
        v_opq_absorbtivity=v_opq_absorbtivity,
        ir_opq_absorbtivity=ir_opq_absorbtivity,
        v_st_absorbtivity=v_st_absorbtivity,
        ir_st_absorbtivity=ir_st_absorbtivity,
        d_st_absorbtivity=d_st_absorbtivity,
        d_transmissivity=d_transmissivity,
        fsi_interface=fsi_interface,
        react=react,
        partially_catalytic=partially_catalytic,
        partially_catalytic_material=partially_catalytic_material,
        partially_catalytic_recombination_coefficient_o=partially_catalytic_recombination_coefficient_o,
        partially_catalytic_recombination_coefficient_n=partially_catalytic_recombination_coefficient_n,
        partially_catalytic_recombination_model=partially_catalytic_recombination_model,
        species_spec=species_spec,
        mf=mf,
        elec_potential_type=elec_potential_type,
        potential_value=potential_value,
        elec_potential_jump=elec_potential_jump,
        elec_potential_resistance=elec_potential_resistance,
        dual_potential_type=dual_potential_type,
        dual_potential_value=dual_potential_value,
        echem_reaction=echem_reaction,
        elec_potential_mechs=elec_potential_mechs,
        faradaic_heat=faradaic_heat,
        li_ion_type=li_ion_type,
        li_ion_value=li_ion_value,
        x_displacement_type=x_displacement_type,
        x_displacement_value=x_displacement_value,
        y_displacement_type=y_displacement_type,
        y_displacement_value=y_displacement_value,
        z_displacement_type=z_displacement_type,
        z_displacement_value=z_displacement_value,
        per_dispx=per_dispx,
        per_dispy=per_dispy,
        per_dispz=per_dispz,
        per_imagx=per_imagx,
        per_imagy=per_imagy,
        per_imagz=per_imagz,
        freq=freq,
        amp=amp,
        nodal_diam=nodal_diam,
        pass_number=pass_number,
        fwd=fwd,
        aero=aero,
        cmplx=cmplx,
        norm=norm,
        method=method_1,
        uds_bc=uds_bc,
        uds=uds,
        gtemp_bc=gtemp_bc,
        g_temperature=g_temperature,
        g_qflux=g_qflux,
        wall_restitution_coeff=wall_restitution_coeff,
        omega=omega,
        origin_position_of_rotation_axis=origin_position_of_rotation_axis,
        direction_component_of_rotation_axis=direction_component_of_rotation_axis,
        adhesion_angle=adhesion_angle,
        specified_shear=specified_shear,
        shear_y=shear_y,
        shear_z=shear_z,
        shear_stress_components=shear_stress_components,
        fslip=fslip,
        eslip=eslip,
        surf_tens_grad=surf_tens_grad,
        contact_resistance=contact_resistance,
        reaction_mechs=reaction_mechs_1,
        surf_washcoat_factor=surf_washcoat_factor,
        ablation_select_model=ablation_select_model,
        ablation_vielle_a=ablation_vielle_a,
        ablation_vielle_n=ablation_vielle_n,
        ablation_surfacerxn_density=ablation_surfacerxn_density,
        ablation_flux=ablation_flux,
        ablation_species_mf=ablation_species_mf,
        specular_coeff=specular_coeff,
        mom_accom_coef=mom_accom_coef,
        therm_accom_coef=therm_accom_coef,
        eve_accom_coef=eve_accom_coef,
        film_wall=film_wall,
        film_wall_bc=film_wall_bc,
        film_height=film_height,
        flux_momentum_components=flux_momentum_components,
        film_relative_vel=film_relative_vel,
        film_bc_imp_press=film_bc_imp_press,
        film_temperature=film_temperature,
        film_scalar=film_scalar,
        film_source=film_source,
        film_h_src=film_h_src,
        film_u_src=film_u_src,
        film_v_src=film_v_src,
        film_w_src=film_w_src,
        momentum_source_components=momentum_source_components,
        film_t_src=film_t_src,
        film_s_src=film_s_src,
        film_phase_change=film_phase_change,
        film_phase_change_model=film_phase_change_model,
        film_cond_const=film_cond_const,
        film_vapo_const=film_vapo_const,
        film_cond_rate=film_cond_rate,
        film_vapo_rate=film_vapo_rate,
        film_momentum_coupling=film_momentum_coupling,
        film_splash_wall=film_splash_wall,
        film_boundary_separation=film_boundary_separation,
        film_impinge_model=film_impinge_model,
        film_splash_nparc=film_splash_nparc,
        film_crit_temp_factor=film_crit_temp_factor,
        film_roughness_ra=film_roughness_ra,
        film_roughness_rz=film_roughness_rz,
        film_upper_deposition_limit_offset=film_upper_deposition_limit_offset,
        film_deposition_delta_t=film_deposition_delta_t,
        film_laplace_number_constant=film_laplace_number_constant,
        film_partial_evap_ratio=film_partial_evap_ratio,
        film_contact_angle=film_contact_angle,
        film_contact_angle_mean=film_contact_angle_mean,
        film_contact_angle_rstd=film_contact_angle_rstd,
        film_contact_angle_beta=film_contact_angle_beta,
        film_vof_coupling_high=film_vof_coupling_high,
        film_vof_trans_high=film_vof_trans_high,
        film_vof_trans_high_relax=film_vof_trans_high_relax,
        film_vof_coupling_low=film_vof_coupling_low,
        film_vof_trans_low=film_vof_trans_low,
        film_vof_trans_low_relax=film_vof_trans_low_relax,
        caf=caf,
        thermal_stabilization=thermal_stabilization,
        scale_factor=scale_factor,
        stab_method=stab_method,
        fensapice_ice_icing_mode=fensapice_ice_icing_mode,
        fensapice_ice_hflux=fensapice_ice_hflux,
        fensapice_ice_hflux_1=fensapice_ice_hflux_1,
        fensapice_drop_vwet=fensapice_drop_vwet,
    )
    return_type = 'object'

class wall(NamedObject[wall_child], CreatableNamedObjectMixinOld[wall_child]):
    """
    'wall' child.
    """
    _version = '222'
    fluent_name = 'wall'
    _python_name = 'wall'
    command_names = ['change_type']
    _child_classes = dict(
        change_type=change_type,
    )
    child_object_type = wall_child
    return_type = 'object'

class boundary_conditions(Group):
    """
    'boundary_conditions' child.
    """
    _version = '222'
    fluent_name = 'boundary-conditions'
    _python_name = 'boundary_conditions'
    child_names = ['axis', 'degassing', 'exhaust_fan', 'fan', 'geometry', 'inlet_vent', 'intake_fan', 'interface', 'interior', 'mass_flow_inlet', 'mass_flow_outlet', 'network', 'network_end', 'outflow', 'outlet_vent', 'overset', 'periodic', 'porous_jump', 'pressure_far_field', 'pressure_inlet', 'pressure_outlet', 'radiator', 'rans_les_interface', 'recirculation_inlet', 'recirculation_outlet', 'shadow', 'symmetry', 'velocity_inlet', 'wall']
    _child_classes = dict(
        axis=axis,
        degassing=degassing,
        exhaust_fan=exhaust_fan,
        fan=fan,
        geometry=geometry,
        inlet_vent=inlet_vent,
        intake_fan=intake_fan,
        interface=interface,
        interior=interior,
        mass_flow_inlet=mass_flow_inlet,
        mass_flow_outlet=mass_flow_outlet,
        network=network,
        network_end=network_end,
        outflow=outflow,
        outlet_vent=outlet_vent,
        overset=overset,
        periodic=periodic,
        porous_jump=porous_jump,
        pressure_far_field=pressure_far_field,
        pressure_inlet=pressure_inlet,
        pressure_outlet=pressure_outlet,
        radiator=radiator,
        rans_les_interface=rans_les_interface,
        recirculation_inlet=recirculation_inlet,
        recirculation_outlet=recirculation_outlet,
        shadow=shadow,
        symmetry=symmetry,
        velocity_inlet=velocity_inlet,
        wall=wall,
    )
    return_type = 'object'

class area(Real):
    """
    Reference area for normalization.
    """
    _version = '222'
    fluent_name = 'area'
    _python_name = 'area'
    return_type = 'object'

class compute_1(Real):
    """
    'compute' child.
    """
    _version = '222'
    fluent_name = 'compute'
    _python_name = 'compute'
    return_type = 'object'

class compute(Group):
    """
    'compute' child.
    """
    _version = '222'
    fluent_name = 'compute'
    _python_name = 'compute'
    child_names = ['compute']
    _child_classes = dict(
        compute=compute_1,
    )
    return_type = 'object'

class depth(Real):
    """
    Reference depth for volume calculation.
    """
    _version = '222'
    fluent_name = 'depth'
    _python_name = 'depth'
    return_type = 'object'

class density_1(Real):
    """
    Reference density for normalization.
    """
    _version = '222'
    fluent_name = 'density'
    _python_name = 'density'
    return_type = 'object'

class enthalpy(Real):
    """
    Reference enthalpy for enthalpy damping and normalization.
    """
    _version = '222'
    fluent_name = 'enthalpy'
    _python_name = 'enthalpy'
    return_type = 'object'

class length_val(Real):
    """
    Reference length for normalization.
    """
    _version = '222'
    fluent_name = 'length-val'
    _python_name = 'length_val'
    return_type = 'object'

class pressure(Real):
    """
    Reference pressure for normalization.
    """
    _version = '222'
    fluent_name = 'pressure'
    _python_name = 'pressure'
    return_type = 'object'

class temperature_1(Real):
    """
    Reference temperature for normalization.
    """
    _version = '222'
    fluent_name = 'temperature'
    _python_name = 'temperature'
    return_type = 'object'

class yplus(Real):
    """
    Reference yplus for normalization.
    """
    _version = '222'
    fluent_name = 'yplus'
    _python_name = 'yplus'
    return_type = 'object'

class velocity(Real):
    """
    Reference velocity for normalization.
    """
    _version = '222'
    fluent_name = 'velocity'
    _python_name = 'velocity'
    return_type = 'object'

class viscosity_1(Real):
    """
    Reference viscosity for normalization.
    """
    _version = '222'
    fluent_name = 'viscosity'
    _python_name = 'viscosity'
    return_type = 'object'

class list_val(Boolean):
    """
    'list_val' child.
    """
    _version = '222'
    fluent_name = 'list-val'
    _python_name = 'list_val'
    return_type = 'object'

class reference_values(Group):
    """
    'reference_values' child.
    """
    _version = '222'
    fluent_name = 'reference-values'
    _python_name = 'reference_values'
    child_names = ['area', 'compute', 'depth', 'density', 'enthalpy', 'length_val', 'pressure', 'temperature', 'yplus', 'velocity', 'viscosity', 'list_val']
    _child_classes = dict(
        area=area,
        compute=compute,
        depth=depth,
        density=density_1,
        enthalpy=enthalpy,
        length_val=length_val,
        pressure=pressure,
        temperature=temperature_1,
        yplus=yplus,
        velocity=velocity,
        viscosity=viscosity_1,
        list_val=list_val,
    )
    return_type = 'object'

class setup(Group):
    """
    'setup' child.
    """
    _version = '222'
    fluent_name = 'setup'
    _python_name = 'setup'
    child_names = ['general', 'models', 'materials', 'cell_zone_conditions', 'boundary_conditions', 'reference_values']
    _child_classes = dict(
        general=general,
        models=models,
        materials=materials,
        cell_zone_conditions=cell_zone_conditions,
        boundary_conditions=boundary_conditions,
        reference_values=reference_values,
    )
    return_type = 'object'

class under_relaxation_factor(Real):
    """
    Under-relaxation factor to be used in .
    """
    _version = '222'
    fluent_name = 'under-relaxation-factor'
    _python_name = 'under_relaxation_factor'
    return_type = 'object'

class explicit_relaxation_factor(Real):
    """
    Explicit relaxation factor to be applied to.
    """
    _version = '222'
    fluent_name = 'explicit-relaxation-factor'
    _python_name = 'explicit_relaxation_factor'
    return_type = 'object'

class expert(Group):
    """
    'expert' child.
    """
    _version = '222'
    fluent_name = 'expert'
    _python_name = 'expert'
    child_names = ['under_relaxation_factor', 'explicit_relaxation_factor']
    _child_classes = dict(
        under_relaxation_factor=under_relaxation_factor,
        explicit_relaxation_factor=explicit_relaxation_factor,
    )
    return_type = 'object'

class relative_convergence_criterion(Real):
    """
    Convergence tolerance for the timestep iterations.
    """
    _version = '222'
    fluent_name = 'relative-convergence-criterion'
    _python_name = 'relative_convergence_criterion'
    return_type = 'object'

class max_iterations_per_timestep(Integer):
    """
    Maximum number of iterations per timestep.
    """
    _version = '222'
    fluent_name = 'max-iterations-per-timestep'
    _python_name = 'max_iterations_per_timestep'
    return_type = 'object'

class acoustics_wave_equation_controls(Group):
    """
    'acoustics_wave_equation_controls' child.
    """
    _version = '222'
    fluent_name = 'acoustics-wave-equation-controls'
    _python_name = 'acoustics_wave_equation_controls'
    child_names = ['expert', 'relative_convergence_criterion', 'max_iterations_per_timestep']
    _child_classes = dict(
        expert=expert,
        relative_convergence_criterion=relative_convergence_criterion,
        max_iterations_per_timestep=max_iterations_per_timestep,
    )
    return_type = 'object'

class cycle_type(String, AllowedValuesMixin):
    """
    'cycle_type' child.
    """
    _version = '222'
    fluent_name = 'cycle-type'
    _python_name = 'cycle_type'
    return_type = 'object'

class termination_criteria(Real):
    """
    'termination_criteria' child.
    """
    _version = '222'
    fluent_name = 'termination-criteria'
    _python_name = 'termination_criteria'
    return_type = 'object'

class residual_reduction_tolerance(Real):
    """
    'residual_reduction_tolerance' child.
    """
    _version = '222'
    fluent_name = 'residual-reduction-tolerance'
    _python_name = 'residual_reduction_tolerance'
    return_type = 'object'

class stabilization(String, AllowedValuesMixin):
    """
    'stabilization' child.
    """
    _version = '222'
    fluent_name = 'stabilization'
    _python_name = 'stabilization'
    return_type = 'object'

class multi_grid_controls_child(Group):
    """
    'child_object_type' of multi_grid_controls.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'multi_grid_controls_child'
    child_names = ['cycle_type', 'termination_criteria', 'residual_reduction_tolerance', 'method', 'stabilization']
    _child_classes = dict(
        cycle_type=cycle_type,
        termination_criteria=termination_criteria,
        residual_reduction_tolerance=residual_reduction_tolerance,
        method=method,
        stabilization=stabilization,
    )
    return_type = 'object'

class multi_grid_controls(NamedObject[multi_grid_controls_child], CreatableNamedObjectMixinOld[multi_grid_controls_child]):
    """
    'multi_grid_controls' child.
    """
    _version = '222'
    fluent_name = 'multi-grid-controls'
    _python_name = 'multi_grid_controls'
    child_object_type = multi_grid_controls_child
    return_type = 'object'

class pre_sweeps(Integer):
    """
    Number of pre-relaxations for fixed cycles.
    """
    _version = '222'
    fluent_name = 'pre-sweeps'
    _python_name = 'pre_sweeps'
    return_type = 'object'

class post_sweeps(Integer):
    """
    Number of post-relaxations for fixed cycles.
    """
    _version = '222'
    fluent_name = 'post-sweeps'
    _python_name = 'post_sweeps'
    return_type = 'object'

class max_cycle(Integer):
    """
    Maximum number of cycles.
    """
    _version = '222'
    fluent_name = 'max-cycle'
    _python_name = 'max_cycle'
    return_type = 'object'

class fixed_cycle_parameters(Group):
    """
    'fixed_cycle_parameters' child.
    """
    _version = '222'
    fluent_name = 'fixed-cycle-parameters'
    _python_name = 'fixed_cycle_parameters'
    child_names = ['pre_sweeps', 'post_sweeps', 'max_cycle']
    _child_classes = dict(
        pre_sweeps=pre_sweeps,
        post_sweeps=post_sweeps,
        max_cycle=max_cycle,
    )
    return_type = 'object'

class max_coarse_levels(Integer):
    """
    Maximum number of coarse grid levels.
    """
    _version = '222'
    fluent_name = 'max-coarse-levels'
    _python_name = 'max_coarse_levels'
    return_type = 'object'

class coarsen_by_interval(Integer):
    """
    Coarsen by interval.
    """
    _version = '222'
    fluent_name = 'coarsen-by-interval'
    _python_name = 'coarsen_by_interval'
    return_type = 'object'

class conservative_coarsening(Boolean):
    """
    Use conservative AMG coarsening?.
    """
    _version = '222'
    fluent_name = 'conservative-coarsening?'
    _python_name = 'conservative_coarsening'
    return_type = 'object'

class aggressive_coarsening(Boolean):
    """
    Enable aggressive AMG coarsening for scalar equation systems.
    """
    _version = '222'
    fluent_name = 'aggressive-coarsening?'
    _python_name = 'aggressive_coarsening'
    return_type = 'object'

class laplace_coarsening(Boolean):
    """
    AMG laplace coarsening options.
    """
    _version = '222'
    fluent_name = 'laplace-coarsening?'
    _python_name = 'laplace_coarsening'
    return_type = 'object'

class coarsening_parameters(Group):
    """
    'coarsening_parameters' child.
    """
    _version = '222'
    fluent_name = 'coarsening-parameters'
    _python_name = 'coarsening_parameters'
    child_names = ['max_coarse_levels', 'coarsen_by_interval', 'conservative_coarsening', 'aggressive_coarsening', 'laplace_coarsening']
    _child_classes = dict(
        max_coarse_levels=max_coarse_levels,
        coarsen_by_interval=coarsen_by_interval,
        conservative_coarsening=conservative_coarsening,
        aggressive_coarsening=aggressive_coarsening,
        laplace_coarsening=laplace_coarsening,
    )
    return_type = 'object'

class smoother_type(String, AllowedValuesMixin):
    """
    Smoother type.
    """
    _version = '222'
    fluent_name = 'smoother-type'
    _python_name = 'smoother_type'
    return_type = 'object'

class scalar_parameters(Group):
    """
    'scalar_parameters' child.
    """
    _version = '222'
    fluent_name = 'scalar-parameters'
    _python_name = 'scalar_parameters'
    child_names = ['fixed_cycle_parameters', 'coarsening_parameters', 'smoother_type']
    _child_classes = dict(
        fixed_cycle_parameters=fixed_cycle_parameters,
        coarsening_parameters=coarsening_parameters,
        smoother_type=smoother_type,
    )
    return_type = 'object'

class pre_sweeps_1(Integer):
    """
    Coupled:number of pre-relaxations for fixed cycles.
    """
    _version = '222'
    fluent_name = 'pre-sweeps'
    _python_name = 'pre_sweeps'
    return_type = 'object'

class post_sweeps_1(Integer):
    """
    Coupled:number of post-relaxations for fixed cycles.
    """
    _version = '222'
    fluent_name = 'post-sweeps'
    _python_name = 'post_sweeps'
    return_type = 'object'

class max_cycle_1(Integer):
    """
    Coupled:maximum number of cycles.
    """
    _version = '222'
    fluent_name = 'max-cycle'
    _python_name = 'max_cycle'
    return_type = 'object'

class fixed_cycle_parameters_1(Group):
    """
    'fixed_cycle_parameters' child.
    """
    _version = '222'
    fluent_name = 'fixed-cycle-parameters'
    _python_name = 'fixed_cycle_parameters'
    child_names = ['pre_sweeps', 'post_sweeps', 'max_cycle']
    _child_classes = dict(
        pre_sweeps=pre_sweeps_1,
        post_sweeps=post_sweeps_1,
        max_cycle=max_cycle_1,
    )
    return_type = 'object'

class max_coarse_levels_1(Integer):
    """
    Coupled:maximum number of coarse grid levels.
    """
    _version = '222'
    fluent_name = 'max-coarse-levels'
    _python_name = 'max_coarse_levels'
    return_type = 'object'

class coarsen_by_interval_1(Integer):
    """
    Coupled:coarsen by interval.
    """
    _version = '222'
    fluent_name = 'coarsen-by-interval'
    _python_name = 'coarsen_by_interval'
    return_type = 'object'

class aggressive_coarsening_1(Boolean):
    """
    Enable aggressive AMG coarsening for coupled equation systems.
    """
    _version = '222'
    fluent_name = 'aggressive-coarsening?'
    _python_name = 'aggressive_coarsening'
    return_type = 'object'

class coarsening_parameters_1(Group):
    """
    'coarsening_parameters' child.
    """
    _version = '222'
    fluent_name = 'coarsening-parameters'
    _python_name = 'coarsening_parameters'
    child_names = ['max_coarse_levels', 'coarsen_by_interval', 'conservative_coarsening', 'aggressive_coarsening', 'laplace_coarsening']
    _child_classes = dict(
        max_coarse_levels=max_coarse_levels_1,
        coarsen_by_interval=coarsen_by_interval_1,
        conservative_coarsening=conservative_coarsening,
        aggressive_coarsening=aggressive_coarsening_1,
        laplace_coarsening=laplace_coarsening,
    )
    return_type = 'object'

class smoother_type_1(String, AllowedValuesMixin):
    """
    Coupled:smoother type.
    """
    _version = '222'
    fluent_name = 'smoother-type'
    _python_name = 'smoother_type'
    return_type = 'object'

class coupled_parameters(Group):
    """
    'coupled_parameters' child.
    """
    _version = '222'
    fluent_name = 'coupled-parameters'
    _python_name = 'coupled_parameters'
    child_names = ['fixed_cycle_parameters', 'coarsening_parameters', 'smoother_type']
    _child_classes = dict(
        fixed_cycle_parameters=fixed_cycle_parameters_1,
        coarsening_parameters=coarsening_parameters_1,
        smoother_type=smoother_type_1,
    )
    return_type = 'object'

class max_fine_relaxations(Integer):
    """
    Maximum number of fine level relaxations for flexible cycle.
    """
    _version = '222'
    fluent_name = 'max-fine-relaxations'
    _python_name = 'max_fine_relaxations'
    return_type = 'object'

class max_coarse_relaxations(Integer):
    """
    Maximum number of coarse level relaxations for flexible cycle.
    """
    _version = '222'
    fluent_name = 'max-coarse-relaxations'
    _python_name = 'max_coarse_relaxations'
    return_type = 'object'

class flexible_cycle_paramters(Group):
    """
    'flexible_cycle_paramters' child.
    """
    _version = '222'
    fluent_name = 'flexible-cycle-paramters'
    _python_name = 'flexible_cycle_paramters'
    child_names = ['max_fine_relaxations', 'max_coarse_relaxations']
    _child_classes = dict(
        max_fine_relaxations=max_fine_relaxations,
        max_coarse_relaxations=max_coarse_relaxations,
    )
    return_type = 'object'

class verbosity(Integer):
    """
    Multigrid verbosity.
    """
    _version = '222'
    fluent_name = 'verbosity'
    _python_name = 'verbosity'
    return_type = 'object'

class options_1(Group):
    """
    'options' child.
    """
    _version = '222'
    fluent_name = 'options'
    _python_name = 'options'
    child_names = ['verbosity']
    _child_classes = dict(
        verbosity=verbosity,
    )
    return_type = 'object'

class algebric_mg_controls(Group):
    """
    'algebric_mg_controls' child.
    """
    _version = '222'
    fluent_name = 'algebric-mg-controls'
    _python_name = 'algebric_mg_controls'
    child_names = ['scalar_parameters', 'coupled_parameters', 'flexible_cycle_paramters', 'options']
    _child_classes = dict(
        scalar_parameters=scalar_parameters,
        coupled_parameters=coupled_parameters,
        flexible_cycle_paramters=flexible_cycle_paramters,
        options=options_1,
    )
    return_type = 'object'

class pre_sweeps_2(Integer):
    """
    Number of fine grid relaxations.
    """
    _version = '222'
    fluent_name = 'pre-sweeps'
    _python_name = 'pre_sweeps'
    return_type = 'object'

class post_sweeps_2(Integer):
    """
    Number of relaxations after interpolation.
    """
    _version = '222'
    fluent_name = 'post-sweeps'
    _python_name = 'post_sweeps'
    return_type = 'object'

class fixed_cycle_parameters_2(Group):
    """
    'fixed_cycle_parameters' child.
    """
    _version = '222'
    fluent_name = 'fixed-cycle-parameters'
    _python_name = 'fixed_cycle_parameters'
    child_names = ['pre_sweeps', 'post_sweeps']
    _child_classes = dict(
        pre_sweeps=pre_sweeps_2,
        post_sweeps=post_sweeps_2,
    )
    return_type = 'object'

class max_coarse_levels_2(Integer):
    """
    Number of coarse grid levels.
    """
    _version = '222'
    fluent_name = 'max-coarse-levels'
    _python_name = 'max_coarse_levels'
    return_type = 'object'

class coarsen_by_interval_2(Integer):
    """
    Coarsen-by interval.
    """
    _version = '222'
    fluent_name = 'coarsen-by-interval'
    _python_name = 'coarsen_by_interval'
    return_type = 'object'

class coarsening_parameters_2(Group):
    """
    'coarsening_parameters' child.
    """
    _version = '222'
    fluent_name = 'coarsening-parameters'
    _python_name = 'coarsening_parameters'
    child_names = ['max_coarse_levels', 'coarsen_by_interval']
    _child_classes = dict(
        max_coarse_levels=max_coarse_levels_2,
        coarsen_by_interval=coarsen_by_interval_2,
    )
    return_type = 'object'

class courant_number_reduction(Real):
    """
    Coarse-grid Courant number reduction factor.
    """
    _version = '222'
    fluent_name = 'courant-number-reduction'
    _python_name = 'courant_number_reduction'
    return_type = 'object'

class correction_reduction(Real):
    """
    Correction relaxation factor.
    """
    _version = '222'
    fluent_name = 'correction-reduction'
    _python_name = 'correction_reduction'
    return_type = 'object'

class correction_smoothing(Real):
    """
    Correction smoothing factor.
    """
    _version = '222'
    fluent_name = 'correction-smoothing'
    _python_name = 'correction_smoothing'
    return_type = 'object'

class species_correction_reduction(Real):
    """
    Species relaxation factor.
    """
    _version = '222'
    fluent_name = 'species-correction-reduction'
    _python_name = 'species_correction_reduction'
    return_type = 'object'

class relaxation_factor_1(Group):
    """
    'relaxation_factor' child.
    """
    _version = '222'
    fluent_name = 'relaxation-factor'
    _python_name = 'relaxation_factor'
    child_names = ['courant_number_reduction', 'correction_reduction', 'correction_smoothing', 'species_correction_reduction']
    _child_classes = dict(
        courant_number_reduction=courant_number_reduction,
        correction_reduction=correction_reduction,
        correction_smoothing=correction_smoothing,
        species_correction_reduction=species_correction_reduction,
    )
    return_type = 'object'

class fas_mg_controls(Group):
    """
    'fas_mg_controls' child.
    """
    _version = '222'
    fluent_name = 'fas-mg-controls'
    _python_name = 'fas_mg_controls'
    child_names = ['fixed_cycle_parameters', 'coarsening_parameters', 'relaxation_factor', 'options']
    _child_classes = dict(
        fixed_cycle_parameters=fixed_cycle_parameters_2,
        coarsening_parameters=coarsening_parameters_2,
        relaxation_factor=relaxation_factor_1,
        options=options_1,
    )
    return_type = 'object'

class enable_gpu(Boolean):
    """
    'enable_gpu' child.
    """
    _version = '222'
    fluent_name = 'enable-gpu?'
    _python_name = 'enable_gpu'
    return_type = 'object'

class term_criterion(Real):
    """
    'term_criterion' child.
    """
    _version = '222'
    fluent_name = 'term-criterion'
    _python_name = 'term_criterion'
    return_type = 'object'

class solver_1(String, AllowedValuesMixin):
    """
    'solver' child.
    """
    _version = '222'
    fluent_name = 'solver'
    _python_name = 'solver'
    return_type = 'object'

class max_num_cycle(Integer):
    """
    'max_num_cycle' child.
    """
    _version = '222'
    fluent_name = 'max-num-cycle'
    _python_name = 'max_num_cycle'
    return_type = 'object'

class coarsen_by_size(Integer):
    """
    'coarsen_by_size' child.
    """
    _version = '222'
    fluent_name = 'coarsen-by-size'
    _python_name = 'coarsen_by_size'
    return_type = 'object'

class pre_sweep(Integer):
    """
    'pre_sweep' child.
    """
    _version = '222'
    fluent_name = 'pre-sweep'
    _python_name = 'pre_sweep'
    return_type = 'object'

class post_sweep(Integer):
    """
    'post_sweep' child.
    """
    _version = '222'
    fluent_name = 'post-sweep'
    _python_name = 'post_sweep'
    return_type = 'object'

class smoother(String):
    """
    'smoother' child.
    """
    _version = '222'
    fluent_name = 'smoother'
    _python_name = 'smoother'
    return_type = 'object'

class amg_gpgpu_options_child(Group):
    """
    'child_object_type' of amg_gpgpu_options.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'amg_gpgpu_options_child'
    child_names = ['enable_gpu', 'term_criterion', 'solver', 'max_num_cycle', 'coarsen_by_size', 'pre_sweep', 'post_sweep', 'smoother']
    _child_classes = dict(
        enable_gpu=enable_gpu,
        term_criterion=term_criterion,
        solver=solver_1,
        max_num_cycle=max_num_cycle,
        coarsen_by_size=coarsen_by_size,
        pre_sweep=pre_sweep,
        post_sweep=post_sweep,
        smoother=smoother,
    )
    return_type = 'object'

class amg_gpgpu_options(NamedObject[amg_gpgpu_options_child], CreatableNamedObjectMixinOld[amg_gpgpu_options_child]):
    """
    'amg_gpgpu_options' child.
    """
    _version = '222'
    fluent_name = 'amg-gpgpu-options'
    _python_name = 'amg_gpgpu_options'
    child_object_type = amg_gpgpu_options_child
    return_type = 'object'

class multi_grid(Group):
    """
    'multi_grid' child.
    """
    _version = '222'
    fluent_name = 'multi-grid'
    _python_name = 'multi_grid'
    child_names = ['multi_grid_controls', 'algebric_mg_controls', 'fas_mg_controls', 'amg_gpgpu_options']
    _child_classes = dict(
        multi_grid_controls=multi_grid_controls,
        algebric_mg_controls=algebric_mg_controls,
        fas_mg_controls=fas_mg_controls,
        amg_gpgpu_options=amg_gpgpu_options,
    )
    return_type = 'object'

class coefficient(Real):
    """
    Multi-stage coefficient.
    """
    _version = '222'
    fluent_name = 'coefficient'
    _python_name = 'coefficient'
    return_type = 'object'

class dissipation(Boolean):
    """
    Update artificial dissipation at stage.
    """
    _version = '222'
    fluent_name = 'dissipation'
    _python_name = 'dissipation'
    return_type = 'object'

class viscous_1(Boolean):
    """
    Update viscous stresses at stage.
    """
    _version = '222'
    fluent_name = 'viscous'
    _python_name = 'viscous'
    return_type = 'object'

class multi_stage_child(Group):
    """
    'child_object_type' of multi_stage.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'multi_stage_child'
    child_names = ['coefficient', 'dissipation', 'viscous']
    _child_classes = dict(
        coefficient=coefficient,
        dissipation=dissipation,
        viscous=viscous_1,
    )
    return_type = 'object'

class multi_stage(ListObject[multi_stage_child]):
    """
    'multi_stage' child.
    """
    _version = '222'
    fluent_name = 'multi-stage'
    _python_name = 'multi_stage'
    child_object_type = multi_stage_child
    return_type = 'object'

class limiter_type(String, AllowedValuesMixin):
    """
    New slope limiter.
    """
    _version = '222'
    fluent_name = 'limiter-type'
    _python_name = 'limiter_type'
    return_type = 'object'

class cell_to_limiting(String, AllowedValuesMixin):
    """
    Cell to face limiting ([no] for cell to cell limiting) .
    """
    _version = '222'
    fluent_name = 'cell-to-limiting'
    _python_name = 'cell_to_limiting'
    return_type = 'object'

class limiter_filter(Boolean):
    """
    Enable limiter filter?.
    """
    _version = '222'
    fluent_name = 'limiter-filter?'
    _python_name = 'limiter_filter'
    return_type = 'object'

class spatial_discretization_limiter(Group):
    """
    'spatial_discretization_limiter' child.
    """
    _version = '222'
    fluent_name = 'spatial-discretization-limiter'
    _python_name = 'spatial_discretization_limiter'
    child_names = ['limiter_type', 'cell_to_limiting', 'limiter_filter']
    _child_classes = dict(
        limiter_type=limiter_type,
        cell_to_limiting=cell_to_limiting,
        limiter_filter=limiter_filter,
    )
    return_type = 'object'

class expert_1(Group):
    """
    'expert' child.
    """
    _version = '222'
    fluent_name = 'expert'
    _python_name = 'expert'
    child_names = ['spatial_discretization_limiter']
    _child_classes = dict(
        spatial_discretization_limiter=spatial_discretization_limiter,
    )
    return_type = 'object'

class two_stage_runge_kutta(Boolean):
    """
    'two_stage_runge_kutta' child.
    """
    _version = '222'
    fluent_name = 'two-stage-runge-kutta?'
    _python_name = 'two_stage_runge_kutta'
    return_type = 'object'

class default_multi_stage_runge_kutta(Boolean):
    """
    'default_multi_stage_runge_kutta' child.
    """
    _version = '222'
    fluent_name = 'default-multi-stage-runge-kutta?'
    _python_name = 'default_multi_stage_runge_kutta'
    return_type = 'object'

class rk2(Group):
    """
    'rk2' child.
    """
    _version = '222'
    fluent_name = 'rk2'
    _python_name = 'rk2'
    child_names = ['two_stage_runge_kutta', 'default_multi_stage_runge_kutta']
    _child_classes = dict(
        two_stage_runge_kutta=two_stage_runge_kutta,
        default_multi_stage_runge_kutta=default_multi_stage_runge_kutta,
    )
    return_type = 'object'

class fast_transient_settings(Group):
    """
    'fast_transient_settings' child.
    """
    _version = '222'
    fluent_name = 'fast-transient-settings'
    _python_name = 'fast_transient_settings'
    child_names = ['rk2']
    _child_classes = dict(
        rk2=rk2,
    )
    return_type = 'object'

class relaxation_method(String):
    """
    The solver relaxation method.
    """
    _version = '222'
    fluent_name = 'relaxation-method'
    _python_name = 'relaxation_method'
    return_type = 'object'

class correction_tolerance_child(Real):
    """
    'child_object_type' of correction_tolerance.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'correction_tolerance_child'
    return_type = 'object'

class correction_tolerance(NamedObject[correction_tolerance_child], CreatableNamedObjectMixinOld[correction_tolerance_child]):
    """
    'correction_tolerance' child.
    """
    _version = '222'
    fluent_name = 'correction-tolerance'
    _python_name = 'correction_tolerance'
    child_object_type = correction_tolerance_child
    return_type = 'object'

class advanced(Group):
    """
    'advanced' child.
    """
    _version = '222'
    fluent_name = 'advanced'
    _python_name = 'advanced'
    child_names = ['multi_grid', 'multi_stage', 'expert', 'fast_transient_settings', 'relaxation_method', 'correction_tolerance']
    _child_classes = dict(
        multi_grid=multi_grid,
        multi_stage=multi_stage,
        expert=expert_1,
        fast_transient_settings=fast_transient_settings,
        relaxation_method=relaxation_method,
        correction_tolerance=correction_tolerance,
    )
    return_type = 'object'

class solution_stabilization(Boolean):
    """
    Automatic solver settings adjustment for solution stabilization during contact process.
    """
    _version = '222'
    fluent_name = 'solution-stabilization?'
    _python_name = 'solution_stabilization'
    return_type = 'object'

class verbosity_1(Integer):
    """
    Verbosity level for contact solution controls.
    """
    _version = '222'
    fluent_name = 'verbosity'
    _python_name = 'verbosity'
    return_type = 'object'

class iterations(Integer):
    """
    Additional iterations to accomodate contact solution stabilization.
    """
    _version = '222'
    fluent_name = 'iterations'
    _python_name = 'iterations'
    return_type = 'object'

class solution_stabilization_persistence(Integer):
    """
    Persistence of the solution stabilization based on events [0-contact based, 1-always on].
    """
    _version = '222'
    fluent_name = 'solution-stabilization-persistence'
    _python_name = 'solution_stabilization_persistence'
    return_type = 'object'

class persistence_fixed_time_steps(Integer):
    """
    Fixed time-steps for solution stabilization persistence after trigger.
    """
    _version = '222'
    fluent_name = 'persistence-fixed-time-steps'
    _python_name = 'persistence_fixed_time_steps'
    return_type = 'object'

class persistence_fixed_duration(Real):
    """
    Fixed time for solution stabilization persistence after trigger.
    """
    _version = '222'
    fluent_name = 'persistence-fixed-duration'
    _python_name = 'persistence_fixed_duration'
    return_type = 'object'

class extrapolation_method(String, AllowedValuesMixin):
    """
    Solution extrapolation method for cells changing status from contact to non-contact.
    """
    _version = '222'
    fluent_name = 'extrapolation-method'
    _python_name = 'extrapolation_method'
    return_type = 'object'

class parameters(Group):
    """
    'parameters' child.
    """
    _version = '222'
    fluent_name = 'parameters'
    _python_name = 'parameters'
    child_names = ['iterations', 'solution_stabilization_persistence', 'persistence_fixed_time_steps', 'persistence_fixed_duration', 'extrapolation_method']
    _child_classes = dict(
        iterations=iterations,
        solution_stabilization_persistence=solution_stabilization_persistence,
        persistence_fixed_time_steps=persistence_fixed_time_steps,
        persistence_fixed_duration=persistence_fixed_duration,
        extrapolation_method=extrapolation_method,
    )
    return_type = 'object'

class first_to_second_order_blending(Real):
    """
    Factor to control first order to second order blending.
    """
    _version = '222'
    fluent_name = 'first-to-second-order-blending'
    _python_name = 'first_to_second_order_blending'
    return_type = 'object'

class first_to_second_order_blending_list(RealList):
    """
    List set factor to control first order to second order blending.
    """
    _version = '222'
    fluent_name = 'first-to-second-order-blending-list'
    _python_name = 'first_to_second_order_blending_list'
    return_type = 'object'

class scheme(Integer):
    """
    Advection scheme for contact event stability.
    """
    _version = '222'
    fluent_name = 'scheme'
    _python_name = 'scheme'
    return_type = 'object'

class flow_skew_diffusion_exclude(Boolean):
    """
    Exclude skew diffusion discretization contribution for momentum.
    """
    _version = '222'
    fluent_name = 'flow-skew-diffusion-exclude?'
    _python_name = 'flow_skew_diffusion_exclude'
    return_type = 'object'

class scalars_skew_diffusion_exclude(Boolean):
    """
    Exclude skew diffusion discretization contribution for scalars.
    """
    _version = '222'
    fluent_name = 'scalars-skew-diffusion-exclude?'
    _python_name = 'scalars_skew_diffusion_exclude'
    return_type = 'object'

class rhie_chow_flux_specify(Boolean):
    """
    Allow specification of the the rhie-chow flux method.
    """
    _version = '222'
    fluent_name = 'rhie-chow-flux-specify?'
    _python_name = 'rhie_chow_flux_specify'
    return_type = 'object'

class rhie_chow_method(Integer):
    """
    The rhie-chow flux method.
    """
    _version = '222'
    fluent_name = 'rhie-chow-method'
    _python_name = 'rhie_chow_method'
    return_type = 'object'

class spatial(Group):
    """
    'spatial' child.
    """
    _version = '222'
    fluent_name = 'spatial'
    _python_name = 'spatial'
    child_names = ['first_to_second_order_blending', 'first_to_second_order_blending_list', 'scheme', 'flow_skew_diffusion_exclude', 'scalars_skew_diffusion_exclude', 'rhie_chow_flux_specify', 'rhie_chow_method']
    _child_classes = dict(
        first_to_second_order_blending=first_to_second_order_blending,
        first_to_second_order_blending_list=first_to_second_order_blending_list,
        scheme=scheme,
        flow_skew_diffusion_exclude=flow_skew_diffusion_exclude,
        scalars_skew_diffusion_exclude=scalars_skew_diffusion_exclude,
        rhie_chow_flux_specify=rhie_chow_flux_specify,
        rhie_chow_method=rhie_chow_method,
    )
    return_type = 'object'

class transient_parameters_specify(Boolean):
    """
    Enable/Disable transient parameter specification.
    """
    _version = '222'
    fluent_name = 'transient-parameters-specify?'
    _python_name = 'transient_parameters_specify'
    return_type = 'object'

class transient_scheme(Integer):
    """
    Temporal scheme to be used.
    """
    _version = '222'
    fluent_name = 'transient-scheme'
    _python_name = 'transient_scheme'
    return_type = 'object'

class time_scale_modification_method(Integer):
    """
    Time scale modification method [0-time-step, 1-cfl].
    """
    _version = '222'
    fluent_name = 'time-scale-modification-method'
    _python_name = 'time_scale_modification_method'
    return_type = 'object'

class time_scale_modification_factor(Real):
    """
    Time-scale modification factor.
    """
    _version = '222'
    fluent_name = 'time-scale-modification-factor'
    _python_name = 'time_scale_modification_factor'
    return_type = 'object'

class transient(Group):
    """
    'transient' child.
    """
    _version = '222'
    fluent_name = 'transient'
    _python_name = 'transient'
    child_names = ['transient_parameters_specify', 'transient_scheme', 'time_scale_modification_method', 'time_scale_modification_factor']
    _child_classes = dict(
        transient_parameters_specify=transient_parameters_specify,
        transient_scheme=transient_scheme,
        time_scale_modification_method=time_scale_modification_method,
        time_scale_modification_factor=time_scale_modification_factor,
    )
    return_type = 'object'

class enforce_laplace_coarsening(Boolean):
    """
    Enable/disable the use of laplace coarsening in AMG.
    """
    _version = '222'
    fluent_name = 'enforce-laplace-coarsening?'
    _python_name = 'enforce_laplace_coarsening'
    return_type = 'object'

class increase_pre_sweeps(Boolean):
    """
    Enable/disable increase in AMG pre-sweeps.
    """
    _version = '222'
    fluent_name = 'increase-pre-sweeps?'
    _python_name = 'increase_pre_sweeps'
    return_type = 'object'

class pre_sweeps_3(Integer):
    """
    The number of AMG pre-sweeps.
    """
    _version = '222'
    fluent_name = 'pre-sweeps'
    _python_name = 'pre_sweeps'
    return_type = 'object'

class specify_coarsening_rate(Boolean):
    """
    Enable/disable AMG coarsening rate.
    """
    _version = '222'
    fluent_name = 'specify-coarsening-rate?'
    _python_name = 'specify_coarsening_rate'
    return_type = 'object'

class coarsen_rate(Integer):
    """
    AMG coarsening rate.
    """
    _version = '222'
    fluent_name = 'coarsen-rate'
    _python_name = 'coarsen_rate'
    return_type = 'object'

class amg(Group):
    """
    'amg' child.
    """
    _version = '222'
    fluent_name = 'amg'
    _python_name = 'amg'
    child_names = ['enforce_laplace_coarsening', 'increase_pre_sweeps', 'pre_sweeps', 'specify_coarsening_rate', 'coarsen_rate']
    _child_classes = dict(
        enforce_laplace_coarsening=enforce_laplace_coarsening,
        increase_pre_sweeps=increase_pre_sweeps,
        pre_sweeps=pre_sweeps_3,
        specify_coarsening_rate=specify_coarsening_rate,
        coarsen_rate=coarsen_rate,
    )
    return_type = 'object'

class model_ramping(Boolean):
    """
    Enable/disable model ramping for solver stability and accuracy.
    """
    _version = '222'
    fluent_name = 'model-ramping?'
    _python_name = 'model_ramping'
    return_type = 'object'

class ramp_flow(Boolean):
    """
    Enable/disable ramp flow for solver stability and accuracy.
    """
    _version = '222'
    fluent_name = 'ramp-flow?'
    _python_name = 'ramp_flow'
    return_type = 'object'

class ramp_turbulence(Boolean):
    """
    Enable/disable ramp turbulence for solver stability and accuracy.
    """
    _version = '222'
    fluent_name = 'ramp-turbulence?'
    _python_name = 'ramp_turbulence'
    return_type = 'object'

class ramp_scalars(Boolean):
    """
    Enable/disable ramp all scalar transport equations for solver stability and accuracy.
    """
    _version = '222'
    fluent_name = 'ramp-scalars?'
    _python_name = 'ramp_scalars'
    return_type = 'object'

class models_2(Group):
    """
    'models' child.
    """
    _version = '222'
    fluent_name = 'models'
    _python_name = 'models'
    child_names = ['model_ramping', 'ramp_flow', 'ramp_turbulence', 'ramp_scalars']
    _child_classes = dict(
        model_ramping=model_ramping,
        ramp_flow=ramp_flow,
        ramp_turbulence=ramp_turbulence,
        ramp_scalars=ramp_scalars,
    )
    return_type = 'object'

class pressure_velocity_coupling_controls(Boolean):
    """
    Enable/disable pressure-velocity coupling method change for solver stability and accuracy.
    """
    _version = '222'
    fluent_name = 'pressure-velocity-coupling-controls?'
    _python_name = 'pressure_velocity_coupling_controls'
    return_type = 'object'

class pressure_velocity_coupling_method(Integer):
    """
    Pressure-velocity coupling method change for solver stability and accuracy.
    """
    _version = '222'
    fluent_name = 'pressure-velocity-coupling-method'
    _python_name = 'pressure_velocity_coupling_method'
    return_type = 'object'

class gradient_controls(Boolean):
    """
    Enable/disable gradient method for solver stability and accuracy.
    """
    _version = '222'
    fluent_name = 'gradient-controls?'
    _python_name = 'gradient_controls'
    return_type = 'object'

class specify_gradient_method(Integer):
    """
    Gradient method for solver stability and accuracy.
    """
    _version = '222'
    fluent_name = 'specify-gradient-method'
    _python_name = 'specify_gradient_method'
    return_type = 'object'

class methods_1(Group):
    """
    'methods' child.
    """
    _version = '222'
    fluent_name = 'methods'
    _python_name = 'methods'
    child_names = ['pressure_velocity_coupling_controls', 'pressure_velocity_coupling_method', 'gradient_controls', 'specify_gradient_method']
    _child_classes = dict(
        pressure_velocity_coupling_controls=pressure_velocity_coupling_controls,
        pressure_velocity_coupling_method=pressure_velocity_coupling_method,
        gradient_controls=gradient_controls,
        specify_gradient_method=specify_gradient_method,
    )
    return_type = 'object'

class compute_statistics(Boolean):
    """
    Enable/disable solution statistics for contact updates.
    """
    _version = '222'
    fluent_name = 'compute-statistics?'
    _python_name = 'compute_statistics'
    return_type = 'object'

class statistics_level(Integer):
    """
    Level of detail for solution statistics.
    """
    _version = '222'
    fluent_name = 'statistics-level'
    _python_name = 'statistics_level'
    return_type = 'object'

class miscellaneous(Group):
    """
    'miscellaneous' child.
    """
    _version = '222'
    fluent_name = 'miscellaneous'
    _python_name = 'miscellaneous'
    child_names = ['compute_statistics', 'statistics_level']
    _child_classes = dict(
        compute_statistics=compute_statistics,
        statistics_level=statistics_level,
    )
    return_type = 'object'

class set_settings_to_default(Command):
    """
    Set contact solution stabilization to default.
    """
    _version = '222'
    fluent_name = 'set-settings-to-default'
    _python_name = 'set_settings_to_default'
    return_type = 'object'

class contact_solution_controls(Group):
    """
    'contact_solution_controls' child.
    """
    _version = '222'
    fluent_name = 'contact-solution-controls'
    _python_name = 'contact_solution_controls'
    child_names = ['solution_stabilization', 'verbosity', 'parameters', 'spatial', 'transient', 'amg', 'models', 'methods', 'miscellaneous']
    command_names = ['set_settings_to_default']
    _child_classes = dict(
        solution_stabilization=solution_stabilization,
        verbosity=verbosity_1,
        parameters=parameters,
        spatial=spatial,
        transient=transient,
        amg=amg,
        models=models_2,
        methods=methods_1,
        miscellaneous=miscellaneous,
        set_settings_to_default=set_settings_to_default,
    )
    return_type = 'object'

class courant_number(Real):
    """
    Courant number.
    """
    _version = '222'
    fluent_name = 'courant-number'
    _python_name = 'courant_number'
    return_type = 'object'

class equations_child(Boolean):
    """
    'child_object_type' of equations.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'equations_child'
    return_type = 'object'

class equations(NamedObject[equations_child], CreatableNamedObjectMixinOld[equations_child]):
    """
    'equations' child.
    """
    _version = '222'
    fluent_name = 'equations'
    _python_name = 'equations'
    child_object_type = equations_child
    return_type = 'object'

class pressure_max_lim(Real):
    """
    Maximum allowable absolute pressure.
    """
    _version = '222'
    fluent_name = 'pressure-max-lim'
    _python_name = 'pressure_max_lim'
    return_type = 'object'

class pressure_min_lim(Real):
    """
    Minimum vapor pressure limit for cavitation model.
    """
    _version = '222'
    fluent_name = 'pressure-min-lim'
    _python_name = 'pressure_min_lim'
    return_type = 'object'

class temperature_max_lim(Real):
    """
    Maximum allowable temperature.
    """
    _version = '222'
    fluent_name = 'temperature-max-lim'
    _python_name = 'temperature_max_lim'
    return_type = 'object'

class temperature_min_lim(Real):
    """
    Minimum allowable temperature.
    """
    _version = '222'
    fluent_name = 'temperature-min-lim'
    _python_name = 'temperature_min_lim'
    return_type = 'object'

class k_min_lim(Real):
    """
    Minimum allowable k.
    """
    _version = '222'
    fluent_name = 'k-min-lim'
    _python_name = 'k_min_lim'
    return_type = 'object'

class k1_min_lim(Real):
    """
    Minimum allowable k1.
    """
    _version = '222'
    fluent_name = 'k1-min-lim'
    _python_name = 'k1_min_lim'
    return_type = 'object'

class des_k_min_lim(Real):
    """
    Minimum allowable k.
    """
    _version = '222'
    fluent_name = 'des-k-min-lim'
    _python_name = 'des_k_min_lim'
    return_type = 'object'

class epsilon_min_lim(Real):
    """
    Minimum allowable epsilon.
    """
    _version = '222'
    fluent_name = 'epsilon-min-lim'
    _python_name = 'epsilon_min_lim'
    return_type = 'object'

class des_epsilon_min_lim(Real):
    """
    Minimum allowable epsilon.
    """
    _version = '222'
    fluent_name = 'des-epsilon-min-lim'
    _python_name = 'des_epsilon_min_lim'
    return_type = 'object'

class v2f_k_min_lim(Real):
    """
    Minimum allowable k.
    """
    _version = '222'
    fluent_name = 'v2f-k-min-lim'
    _python_name = 'v2f_k_min_lim'
    return_type = 'object'

class v2f_epsilon_min_lim(Real):
    """
    Minimum allowable epsilon.
    """
    _version = '222'
    fluent_name = 'v2f-epsilon-min-lim'
    _python_name = 'v2f_epsilon_min_lim'
    return_type = 'object'

class v2f_v2_min_lim(Real):
    """
    Minimum allowable v2.
    """
    _version = '222'
    fluent_name = 'v2f-v2-min-lim'
    _python_name = 'v2f_v2_min_lim'
    return_type = 'object'

class v2f_f_min_lim(Real):
    """
    Minimum allowable f.
    """
    _version = '222'
    fluent_name = 'v2f-f-min-lim'
    _python_name = 'v2f_f_min_lim'
    return_type = 'object'

class omega_min_lim(Real):
    """
    Minimum allowable omega.
    """
    _version = '222'
    fluent_name = 'omega-min-lim'
    _python_name = 'omega_min_lim'
    return_type = 'object'

class des_omega_min_lim(Real):
    """
    Minimum allowable omega.
    """
    _version = '222'
    fluent_name = 'des-omega-min-lim'
    _python_name = 'des_omega_min_lim'
    return_type = 'object'

class turb_visc_max_lim(Real):
    """
    Maximum allowable turbulent/laminar viscosity ratio.
    """
    _version = '222'
    fluent_name = 'turb-visc-max-lim'
    _python_name = 'turb_visc_max_lim'
    return_type = 'object'

class pos_lim(Real):
    """
    Positivity Rate Limit.
    """
    _version = '222'
    fluent_name = 'pos-lim'
    _python_name = 'pos_lim'
    return_type = 'object'

class matrix_solv_min_lim(Real):
    """
    Minimum Vol. Frac. for Matrix Solution.
    """
    _version = '222'
    fluent_name = 'matrix-solv-min-lim'
    _python_name = 'matrix_solv_min_lim'
    return_type = 'object'

class limits(Group):
    """
    'limits' child.
    """
    _version = '222'
    fluent_name = 'limits'
    _python_name = 'limits'
    child_names = ['pressure_max_lim', 'pressure_min_lim', 'temperature_max_lim', 'temperature_min_lim', 'k_min_lim', 'k1_min_lim', 'des_k_min_lim', 'epsilon_min_lim', 'des_epsilon_min_lim', 'v2f_k_min_lim', 'v2f_epsilon_min_lim', 'v2f_v2_min_lim', 'v2f_f_min_lim', 'omega_min_lim', 'des_omega_min_lim', 'turb_visc_max_lim', 'pos_lim', 'matrix_solv_min_lim']
    _child_classes = dict(
        pressure_max_lim=pressure_max_lim,
        pressure_min_lim=pressure_min_lim,
        temperature_max_lim=temperature_max_lim,
        temperature_min_lim=temperature_min_lim,
        k_min_lim=k_min_lim,
        k1_min_lim=k1_min_lim,
        des_k_min_lim=des_k_min_lim,
        epsilon_min_lim=epsilon_min_lim,
        des_epsilon_min_lim=des_epsilon_min_lim,
        v2f_k_min_lim=v2f_k_min_lim,
        v2f_epsilon_min_lim=v2f_epsilon_min_lim,
        v2f_v2_min_lim=v2f_v2_min_lim,
        v2f_f_min_lim=v2f_f_min_lim,
        omega_min_lim=omega_min_lim,
        des_omega_min_lim=des_omega_min_lim,
        turb_visc_max_lim=turb_visc_max_lim,
        pos_lim=pos_lim,
        matrix_solv_min_lim=matrix_solv_min_lim,
    )
    return_type = 'object'

class skewness_correction_itr(Integer):
    """
    Iterations for skewness correction.
    """
    _version = '222'
    fluent_name = 'skewness-correction-itr'
    _python_name = 'skewness_correction_itr'
    return_type = 'object'

class neighbor_correction_itr(Integer):
    """
    Iterations for neighbor correction.
    """
    _version = '222'
    fluent_name = 'neighbor-correction-itr'
    _python_name = 'neighbor_correction_itr'
    return_type = 'object'

class skewness_neighbor_coupling(Boolean):
    """
    Skewness-Neighbor Coupling?.
    """
    _version = '222'
    fluent_name = 'skewness-neighbor-coupling'
    _python_name = 'skewness_neighbor_coupling'
    return_type = 'object'

class vof_correction_itr(Integer):
    """
    Iterations for vof correction.
    """
    _version = '222'
    fluent_name = 'vof-correction-itr'
    _python_name = 'vof_correction_itr'
    return_type = 'object'

class explicit_momentum_under_relaxation(Real):
    """
    Explicit momentum under-relaxation.
    """
    _version = '222'
    fluent_name = 'explicit-momentum-under-relaxation'
    _python_name = 'explicit_momentum_under_relaxation'
    return_type = 'object'

class explicit_pressure_under_relaxation(Real):
    """
    Explicit pressure under-relaxation.
    """
    _version = '222'
    fluent_name = 'explicit-pressure-under-relaxation'
    _python_name = 'explicit_pressure_under_relaxation'
    return_type = 'object'

class flow_courant_number(Real):
    """
    'flow_courant_number' child.
    """
    _version = '222'
    fluent_name = 'flow-courant-number'
    _python_name = 'flow_courant_number'
    return_type = 'object'

class volume_fraction_courant_number(Real):
    """
    'volume_fraction_courant_number' child.
    """
    _version = '222'
    fluent_name = 'volume-fraction-courant-number'
    _python_name = 'volume_fraction_courant_number'
    return_type = 'object'

class explicit_volume_fraction_under_relaxation(Real):
    """
    Explicit volume fraction under-relaxation.
    """
    _version = '222'
    fluent_name = 'explicit-volume-fraction-under-relaxation'
    _python_name = 'explicit_volume_fraction_under_relaxation'
    return_type = 'object'

class p_v_controls(Group):
    """
    'p_v_controls' child.
    """
    _version = '222'
    fluent_name = 'p-v-controls'
    _python_name = 'p_v_controls'
    child_names = ['skewness_correction_itr', 'neighbor_correction_itr', 'skewness_neighbor_coupling', 'vof_correction_itr', 'explicit_momentum_under_relaxation', 'explicit_pressure_under_relaxation', 'flow_courant_number', 'volume_fraction_courant_number', 'explicit_volume_fraction_under_relaxation']
    _child_classes = dict(
        skewness_correction_itr=skewness_correction_itr,
        neighbor_correction_itr=neighbor_correction_itr,
        skewness_neighbor_coupling=skewness_neighbor_coupling,
        vof_correction_itr=vof_correction_itr,
        explicit_momentum_under_relaxation=explicit_momentum_under_relaxation,
        explicit_pressure_under_relaxation=explicit_pressure_under_relaxation,
        flow_courant_number=flow_courant_number,
        volume_fraction_courant_number=volume_fraction_courant_number,
        explicit_volume_fraction_under_relaxation=explicit_volume_fraction_under_relaxation,
    )
    return_type = 'object'

class relaxation_factor_child(Real):
    """
    'child_object_type' of relaxation_factor.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'relaxation_factor_child'
    return_type = 'object'

class relaxation_factor(NamedObject[relaxation_factor_child], CreatableNamedObjectMixinOld[relaxation_factor_child]):
    """
    'relaxation_factor' child.
    """
    _version = '222'
    fluent_name = 'relaxation-factor'
    _python_name = 'relaxation_factor'
    child_object_type = relaxation_factor_child
    return_type = 'object'

class solution_controls(Command):
    """
    'solution_controls' command.
    """
    _version = '222'
    fluent_name = 'solution-controls'
    _python_name = 'solution_controls'
    return_type = 'object'

class amg_controls(Command):
    """
    'amg_controls' command.
    """
    _version = '222'
    fluent_name = 'amg-controls'
    _python_name = 'amg_controls'
    return_type = 'object'

class multi_stage_parameter(Command):
    """
    'multi_stage_parameter' command.
    """
    _version = '222'
    fluent_name = 'multi-stage-parameter'
    _python_name = 'multi_stage_parameter'
    return_type = 'object'

class limits_1(Command):
    """
    'limits' command.
    """
    _version = '222'
    fluent_name = 'limits'
    _python_name = 'limits'
    return_type = 'object'

class reset_pseudo_time_method_generic(Command):
    """
    'reset_pseudo_time_method_generic' command.
    """
    _version = '222'
    fluent_name = 'reset-pseudo-time-method-generic'
    _python_name = 'reset_pseudo_time_method_generic'
    return_type = 'object'

class reset_pseudo_time_method_equations(Command):
    """
    'reset_pseudo_time_method_equations' command.
    """
    _version = '222'
    fluent_name = 'reset-pseudo-time-method-equations'
    _python_name = 'reset_pseudo_time_method_equations'
    return_type = 'object'

class reset_pseudo_time_method_relaxations(Command):
    """
    'reset_pseudo_time_method_relaxations' command.
    """
    _version = '222'
    fluent_name = 'reset-pseudo-time-method-relaxations'
    _python_name = 'reset_pseudo_time_method_relaxations'
    return_type = 'object'

class reset_pseudo_time_method_scale_factors(Command):
    """
    'reset_pseudo_time_method_scale_factors' command.
    """
    _version = '222'
    fluent_name = 'reset-pseudo-time-method-scale-factors'
    _python_name = 'reset_pseudo_time_method_scale_factors'
    return_type = 'object'

class set_controls_to_default(Group):
    """
    'set_controls_to_default' child.
    """
    _version = '222'
    fluent_name = 'set-controls-to-default'
    _python_name = 'set_controls_to_default'
    command_names = ['solution_controls', 'amg_controls', 'multi_stage_parameter', 'limits', 'reset_pseudo_time_method_generic', 'reset_pseudo_time_method_equations', 'reset_pseudo_time_method_relaxations', 'reset_pseudo_time_method_scale_factors']
    _child_classes = dict(
        solution_controls=solution_controls,
        amg_controls=amg_controls,
        multi_stage_parameter=multi_stage_parameter,
        limits=limits_1,
        reset_pseudo_time_method_generic=reset_pseudo_time_method_generic,
        reset_pseudo_time_method_equations=reset_pseudo_time_method_equations,
        reset_pseudo_time_method_relaxations=reset_pseudo_time_method_relaxations,
        reset_pseudo_time_method_scale_factors=reset_pseudo_time_method_scale_factors,
    )
    return_type = 'object'

class under_relaxation_child(Real):
    """
    'child_object_type' of under_relaxation.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'under_relaxation_child'
    return_type = 'object'

class under_relaxation(NamedObject[under_relaxation_child], CreatableNamedObjectMixinOld[under_relaxation_child]):
    """
    Under Relaxation Menu.
    """
    _version = '222'
    fluent_name = 'under-relaxation'
    _python_name = 'under_relaxation'
    child_object_type = under_relaxation_child
    return_type = 'object'

class controls(Group):
    """
    'controls' child.
    """
    _version = '222'
    fluent_name = 'controls'
    _python_name = 'controls'
    child_names = ['acoustics_wave_equation_controls', 'advanced', 'contact_solution_controls', 'courant_number', 'equations', 'limits', 'p_v_controls', 'relaxation_factor', 'set_controls_to_default', 'under_relaxation']
    _child_classes = dict(
        acoustics_wave_equation_controls=acoustics_wave_equation_controls,
        advanced=advanced,
        contact_solution_controls=contact_solution_controls,
        courant_number=courant_number,
        equations=equations,
        limits=limits,
        p_v_controls=p_v_controls,
        relaxation_factor=relaxation_factor,
        set_controls_to_default=set_controls_to_default,
        under_relaxation=under_relaxation,
    )
    return_type = 'object'

class accelerated_non_iterative_time_marching(Boolean):
    """
    Enable/disable accelerated non-iterative time marching.
    """
    _version = '222'
    fluent_name = 'accelerated-non-iterative-time-marching?'
    _python_name = 'accelerated_non_iterative_time_marching'
    return_type = 'object'

class convergence_acc_std_meshes(Boolean):
    """
    Enable/disable use of convergence acceleration for stretched meshes (CASM).
    """
    _version = '222'
    fluent_name = 'convergence-acc-std-meshes?'
    _python_name = 'convergence_acc_std_meshes'
    return_type = 'object'

class enhanced_casm_formulation(Boolean):
    """
    Enable/disable use of enhanced CASM formulation.
    """
    _version = '222'
    fluent_name = 'enhanced-casm-formulation?'
    _python_name = 'enhanced_casm_formulation'
    return_type = 'object'

class casm_cutoff_multiplier(Real):
    """
    CASM cut-off multiplier :.
    """
    _version = '222'
    fluent_name = 'casm-cutoff-multiplier'
    _python_name = 'casm_cutoff_multiplier'
    return_type = 'object'

class disable_casm(Command):
    """
    'disable_casm' command.
    """
    _version = '222'
    fluent_name = 'disable-casm'
    _python_name = 'disable_casm'
    return_type = 'object'

class convergence_acceleration_for_stretched_meshes(Group):
    """
    'convergence_acceleration_for_stretched_meshes' child.
    """
    _version = '222'
    fluent_name = 'convergence-acceleration-for-stretched-meshes'
    _python_name = 'convergence_acceleration_for_stretched_meshes'
    child_names = ['convergence_acc_std_meshes', 'enhanced_casm_formulation', 'casm_cutoff_multiplier']
    command_names = ['disable_casm']
    _child_classes = dict(
        convergence_acc_std_meshes=convergence_acc_std_meshes,
        enhanced_casm_formulation=enhanced_casm_formulation,
        casm_cutoff_multiplier=casm_cutoff_multiplier,
        disable_casm=disable_casm,
    )
    return_type = 'object'

class discretization_scheme_child(String, AllowedValuesMixin):
    """
    'child_object_type' of discretization_scheme.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'discretization_scheme_child'
    return_type = 'object'

class discretization_scheme(NamedObject[discretization_scheme_child], CreatableNamedObjectMixinOld[discretization_scheme_child]):
    """
    'discretization_scheme' child.
    """
    _version = '222'
    fluent_name = 'discretization-scheme'
    _python_name = 'discretization_scheme'
    child_object_type = discretization_scheme_child
    return_type = 'object'

class reactions_1(Boolean):
    """
    Enable/disable the species reaction sources and set relaxation factor.
    """
    _version = '222'
    fluent_name = 'reactions?'
    _python_name = 'reactions'
    return_type = 'object'

class reaction_source_term_relaxation_factor(Real):
    """
    Reaction source term relaxation factor.
    """
    _version = '222'
    fluent_name = 'reaction-source-term-relaxation-factor'
    _python_name = 'reaction_source_term_relaxation_factor'
    return_type = 'object'

class implicit_bodyforce_treatment(Boolean):
    """
    Enable/disable implicit body force treatment.
    """
    _version = '222'
    fluent_name = 'implicit-bodyforce-treatment?'
    _python_name = 'implicit_bodyforce_treatment'
    return_type = 'object'

class physical_velocity_formulation(Boolean):
    """
    Enable/disable use of physical velocity formulation for porous media.
    """
    _version = '222'
    fluent_name = 'physical-velocity-formulation?'
    _python_name = 'physical_velocity_formulation'
    return_type = 'object'

class disable_rhie_chow_flux(Boolean):
    """
    Use low order velocity interpolation in flux calculation.
    """
    _version = '222'
    fluent_name = 'disable-rhie-chow-flux?'
    _python_name = 'disable_rhie_chow_flux'
    return_type = 'object'

class presto_pressure_scheme(Boolean):
    """
    Limit high-order terms for PRESTO! pressure scheme.
    """
    _version = '222'
    fluent_name = 'presto-pressure-scheme?'
    _python_name = 'presto_pressure_scheme'
    return_type = 'object'

class first_to_second_order_blending_1(Real):
    """
    1st-order to higher-order blending factor [min=0.0 - max=1.0].
    """
    _version = '222'
    fluent_name = 'first-to-second-order-blending'
    _python_name = 'first_to_second_order_blending'
    return_type = 'object'

class alternate_diffusion_for_porous_region_solids(Boolean):
    """
    Enable/disable use of alternate diffusion for porous region solids.
    """
    _version = '222'
    fluent_name = 'alternate-diffusion-for-porous-region-solids?'
    _python_name = 'alternate_diffusion_for_porous_region_solids'
    return_type = 'object'

class numerics(Group):
    """
    'numerics' child.
    """
    _version = '222'
    fluent_name = 'numerics'
    _python_name = 'numerics'
    child_names = ['implicit_bodyforce_treatment', 'velocity_formulation', 'physical_velocity_formulation', 'disable_rhie_chow_flux', 'presto_pressure_scheme', 'first_to_second_order_blending', 'alternate_diffusion_for_porous_region_solids']
    _child_classes = dict(
        implicit_bodyforce_treatment=implicit_bodyforce_treatment,
        velocity_formulation=velocity_formulation,
        physical_velocity_formulation=physical_velocity_formulation,
        disable_rhie_chow_flux=disable_rhie_chow_flux,
        presto_pressure_scheme=presto_pressure_scheme,
        first_to_second_order_blending=first_to_second_order_blending_1,
        alternate_diffusion_for_porous_region_solids=alternate_diffusion_for_porous_region_solids,
    )
    return_type = 'object'

class first_to_second_order_blending_dbns(Real):
    """
    1st-order to higher-order blending factor [min=0.0 - max=1.0]:.
    """
    _version = '222'
    fluent_name = 'first-to-second-order-blending-dbns'
    _python_name = 'first_to_second_order_blending_dbns'
    return_type = 'object'

class numerics_dbns(Group):
    """
    'numerics_dbns' child.
    """
    _version = '222'
    fluent_name = 'numerics-dbns'
    _python_name = 'numerics_dbns'
    child_names = ['first_to_second_order_blending_dbns']
    _child_classes = dict(
        first_to_second_order_blending_dbns=first_to_second_order_blending_dbns,
    )
    return_type = 'object'

class expert_2(Group):
    """
    'expert' child.
    """
    _version = '222'
    fluent_name = 'expert'
    _python_name = 'expert'
    child_names = ['reactions', 'reaction_source_term_relaxation_factor', 'numerics', 'numerics_dbns']
    _child_classes = dict(
        reactions=reactions_1,
        reaction_source_term_relaxation_factor=reaction_source_term_relaxation_factor,
        numerics=numerics,
        numerics_dbns=numerics_dbns,
    )
    return_type = 'object'

class flux_type_1(String, AllowedValuesMixin):
    """
    Flux Type.
    """
    _version = '222'
    fluent_name = 'flux-type'
    _python_name = 'flux_type'
    return_type = 'object'

class dbns_cases(Group):
    """
    'dbns_cases' child.
    """
    _version = '222'
    fluent_name = 'dbns_cases'
    _python_name = 'dbns_cases'
    child_names = ['flux_type']
    _child_classes = dict(
        flux_type=flux_type_1,
    )
    return_type = 'object'

class flux_auto_select(Boolean):
    """
    Enable/disable Auto Select .
    """
    _version = '222'
    fluent_name = 'flux-auto-select?'
    _python_name = 'flux_auto_select'
    return_type = 'object'

class flux_type_2(Integer):
    """
    'flux_type' child.
    """
    _version = '222'
    fluent_name = 'flux-type'
    _python_name = 'flux_type'
    return_type = 'object'

class pbns_cases(Group):
    """
    'pbns_cases' child.
    """
    _version = '222'
    fluent_name = 'pbns_cases'
    _python_name = 'pbns_cases'
    child_names = ['flux_auto_select', 'flux_type']
    _child_classes = dict(
        flux_auto_select=flux_auto_select,
        flux_type=flux_type_2,
    )
    return_type = 'object'

class flux_type(Group):
    """
    'flux_type' child.
    """
    _version = '222'
    fluent_name = 'flux-type'
    _python_name = 'flux_type'
    child_names = ['dbns_cases', 'pbns_cases']
    _child_classes = dict(
        dbns_cases=dbns_cases,
        pbns_cases=pbns_cases,
    )
    return_type = 'object'

class frozen_flux(Boolean):
    """
    Enable/disable frozen flux formulation for transient flows.
    """
    _version = '222'
    fluent_name = 'frozen-flux?'
    _python_name = 'frozen_flux'
    return_type = 'object'

class gradient_scheme(String, AllowedValuesMixin):
    """
    Gradient scheme.
    """
    _version = '222'
    fluent_name = 'gradient-scheme'
    _python_name = 'gradient_scheme'
    return_type = 'object'

class enable(Boolean):
    """
    Enable/Disable.
    """
    _version = '222'
    fluent_name = 'enable?'
    _python_name = 'enable'
    return_type = 'object'

class relaxation_factor_2(Real):
    """
    Relaxation factor.
    """
    _version = '222'
    fluent_name = 'relaxation-factor'
    _python_name = 'relaxation_factor'
    return_type = 'object'

class select_variables(String, AllowedValuesMixin):
    """
    Variables for high order term relaxation.
    """
    _version = '222'
    fluent_name = 'select-variables'
    _python_name = 'select_variables'
    return_type = 'object'

class relaxation_options(String, AllowedValuesMixin):
    """
    High order relaxation option with respect to diffusion gradient.
    """
    _version = '222'
    fluent_name = 'relaxation-options'
    _python_name = 'relaxation_options'
    return_type = 'object'

class options_2(Group):
    """
    'options' child.
    """
    _version = '222'
    fluent_name = 'options'
    _python_name = 'options'
    child_names = ['relaxation_factor', 'select_variables', 'relaxation_options']
    _child_classes = dict(
        relaxation_factor=relaxation_factor_2,
        select_variables=select_variables,
        relaxation_options=relaxation_options,
    )
    return_type = 'object'

class high_order_term_relaxation(Group):
    """
    'high_order_term_relaxation' child.
    """
    _version = '222'
    fluent_name = 'high-order-term-relaxation'
    _python_name = 'high_order_term_relaxation'
    child_names = ['enable', 'options']
    _child_classes = dict(
        enable=enable,
        options=options_2,
    )
    return_type = 'object'

class relative_permeability(Boolean):
    """
    Multiphase relative permeability fix option.
    """
    _version = '222'
    fluent_name = 'relative-permeability?'
    _python_name = 'relative_permeability'
    return_type = 'object'

class porous_media(Group):
    """
    'porous_media' child.
    """
    _version = '222'
    fluent_name = 'porous-media'
    _python_name = 'porous_media'
    child_names = ['relative_permeability']
    _child_classes = dict(
        relative_permeability=relative_permeability,
    )
    return_type = 'object'

class enhanced_numerics(Boolean):
    """
    Multiphase enhanced compressible flow numerics options.
    """
    _version = '222'
    fluent_name = 'enhanced-numerics?'
    _python_name = 'enhanced_numerics'
    return_type = 'object'

class alternate_bc_formulation(Boolean):
    """
    Enable/disable use of alternate compressible bc formulation.
    """
    _version = '222'
    fluent_name = 'alternate-bc-formulation?'
    _python_name = 'alternate_bc_formulation'
    return_type = 'object'

class analytical_thermodynamic_derivatives(Boolean):
    """
    Enable/disable use of analytical thermodynamic derivatives.
    """
    _version = '222'
    fluent_name = 'analytical-thermodynamic-derivatives?'
    _python_name = 'analytical_thermodynamic_derivatives'
    return_type = 'object'

class compressible_flow(Group):
    """
    'compressible_flow' child.
    """
    _version = '222'
    fluent_name = 'compressible-flow'
    _python_name = 'compressible_flow'
    child_names = ['enhanced_numerics', 'alternate_bc_formulation', 'analytical_thermodynamic_derivatives']
    _child_classes = dict(
        enhanced_numerics=enhanced_numerics,
        alternate_bc_formulation=alternate_bc_formulation,
        analytical_thermodynamic_derivatives=analytical_thermodynamic_derivatives,
    )
    return_type = 'object'

class thin_film(Boolean):
    """
    Multiphase enhanced compressible flow numerics options.
    """
    _version = '222'
    fluent_name = 'thin-film?'
    _python_name = 'thin_film'
    return_type = 'object'

class liquid_vof_factor(Boolean):
    """
    Multiphase enhanced compressible flow numerics options.
    """
    _version = '222'
    fluent_name = 'liquid-vof-factor?'
    _python_name = 'liquid_vof_factor'
    return_type = 'object'

class boiling_parameters(Group):
    """
    'boiling_parameters' child.
    """
    _version = '222'
    fluent_name = 'boiling-parameters'
    _python_name = 'boiling_parameters'
    child_names = ['thin_film', 'liquid_vof_factor']
    _child_classes = dict(
        thin_film=thin_film,
        liquid_vof_factor=liquid_vof_factor,
    )
    return_type = 'object'

class viscosity_averaging(Boolean):
    """
    Enable/disable use of harmonic averaging for viscosity.
    """
    _version = '222'
    fluent_name = 'viscosity-averaging?'
    _python_name = 'viscosity_averaging'
    return_type = 'object'

class turb_visc_based_damping(Boolean):
    """
    Enable/disable turbulence damping based on turbulent viscosity.
    """
    _version = '222'
    fluent_name = 'turb-visc-based-damping?'
    _python_name = 'turb_visc_based_damping'
    return_type = 'object'

class density_func_expo(Real):
    """
    Density function exponent.
    """
    _version = '222'
    fluent_name = 'density-func-expo'
    _python_name = 'density_func_expo'
    return_type = 'object'

class density_ratio_cutoff(Real):
    """
    Density ratio cut-off.
    """
    _version = '222'
    fluent_name = 'density-ratio-cutoff'
    _python_name = 'density_ratio_cutoff'
    return_type = 'object'

class n_smooth_for_interfacial_regims(Integer):
    """
    Number of smoothings for interfacial regime.
    """
    _version = '222'
    fluent_name = 'n-smooth-for-interfacial-regims'
    _python_name = 'n_smooth_for_interfacial_regims'
    return_type = 'object'

class sm_relax_factor(Real):
    """
    Smoothing relaxation factor.
    """
    _version = '222'
    fluent_name = 'sm-relax-factor'
    _python_name = 'sm_relax_factor'
    return_type = 'object'

class viscous_func_options(Integer):
    """
    Viscous function option.
    """
    _version = '222'
    fluent_name = 'viscous-func-options'
    _python_name = 'viscous_func_options'
    return_type = 'object'

class density_func_options(Integer):
    """
    Density function option.
    """
    _version = '222'
    fluent_name = 'density-func-options'
    _python_name = 'density_func_options'
    return_type = 'object'

class exponent_smoothing_func(Real):
    """
    Exponent of smoothing function.
    """
    _version = '222'
    fluent_name = 'exponent-smoothing-func'
    _python_name = 'exponent_smoothing_func'
    return_type = 'object'

class exponent_density_func(Real):
    """
    Exponent of density function.
    """
    _version = '222'
    fluent_name = 'exponent-density-func'
    _python_name = 'exponent_density_func'
    return_type = 'object'

class boundry_treatment(Boolean):
    """
    Enable/disable boundary treatment.
    """
    _version = '222'
    fluent_name = 'boundry-treatment?'
    _python_name = 'boundry_treatment'
    return_type = 'object'

class near_wall_treatment_1(Boolean):
    """
    Enable/disable near wall treatment?.
    """
    _version = '222'
    fluent_name = 'near-wall-treatment?'
    _python_name = 'near_wall_treatment'
    return_type = 'object'

class interfacial_artificial_viscosity(Group):
    """
    'interfacial_artificial_viscosity' child.
    """
    _version = '222'
    fluent_name = 'interfacial-artificial-viscosity'
    _python_name = 'interfacial_artificial_viscosity'
    child_names = ['n_smooth_for_interfacial_regims', 'sm_relax_factor', 'viscous_func_options', 'density_func_options', 'exponent_smoothing_func', 'exponent_density_func', 'boundry_treatment', 'near_wall_treatment']
    _child_classes = dict(
        n_smooth_for_interfacial_regims=n_smooth_for_interfacial_regims,
        sm_relax_factor=sm_relax_factor,
        viscous_func_options=viscous_func_options,
        density_func_options=density_func_options,
        exponent_smoothing_func=exponent_smoothing_func,
        exponent_density_func=exponent_density_func,
        boundry_treatment=boundry_treatment,
        near_wall_treatment=near_wall_treatment_1,
    )
    return_type = 'object'

class viscous_flow(Group):
    """
    'viscous_flow' child.
    """
    _version = '222'
    fluent_name = 'viscous-flow'
    _python_name = 'viscous_flow'
    child_names = ['viscosity_averaging', 'turb_visc_based_damping', 'density_func_expo', 'density_ratio_cutoff', 'interfacial_artificial_viscosity']
    _child_classes = dict(
        viscosity_averaging=viscosity_averaging,
        turb_visc_based_damping=turb_visc_based_damping,
        density_func_expo=density_func_expo,
        density_ratio_cutoff=density_ratio_cutoff,
        interfacial_artificial_viscosity=interfacial_artificial_viscosity,
    )
    return_type = 'object'

class schnerr_evap_coeff(Real):
    """
    Evaporation coefficient for Schnerr-Sauer model.
    """
    _version = '222'
    fluent_name = 'schnerr-evap-coeff'
    _python_name = 'schnerr_evap_coeff'
    return_type = 'object'

class schnerr_cond_coeff(Real):
    """
    Condensation coefficient for Schnerr-Sauer model.
    """
    _version = '222'
    fluent_name = 'schnerr-cond-coeff'
    _python_name = 'schnerr_cond_coeff'
    return_type = 'object'

class max_vapor_pressure_ratio(Real):
    """
    Maximum ratio limit for corrected vapor pressure.
    """
    _version = '222'
    fluent_name = 'max-vapor-pressure-ratio'
    _python_name = 'max_vapor_pressure_ratio'
    return_type = 'object'

class min_vapor_pressure(Real):
    """
    Minimum vapor pressure limit for cavitation model.
    """
    _version = '222'
    fluent_name = 'min-vapor-pressure'
    _python_name = 'min_vapor_pressure'
    return_type = 'object'

class display_clipped_pressure(Boolean):
    """
    Clipped pressure is just used for the properties evaluation. Mass Transfer Rate uses unclipped pressure.
    """
    _version = '222'
    fluent_name = 'display-clipped-pressure?'
    _python_name = 'display_clipped_pressure'
    return_type = 'object'

class turbulent_diffusion(Boolean):
    """
    New turbulent diffusion treatment is applicable to N-phase flow when one of the phases 
    participating in cavitation is selected as a primary phase.
    """
    _version = '222'
    fluent_name = 'turbulent-diffusion?'
    _python_name = 'turbulent_diffusion'
    return_type = 'object'

class old_treatment_for_turbulent_diffusion(Boolean):
    """
    Old turbulent diffusion treatment is applicable to two phase flow when vapor is selected as a secondary phase.
    """
    _version = '222'
    fluent_name = 'old-treatment-for-turbulent-diffusion?'
    _python_name = 'old_treatment_for_turbulent_diffusion'
    return_type = 'object'

class cavitation(Group):
    """
    'cavitation' child.
    """
    _version = '222'
    fluent_name = 'cavitation'
    _python_name = 'cavitation'
    child_names = ['schnerr_evap_coeff', 'schnerr_cond_coeff', 'max_vapor_pressure_ratio', 'min_vapor_pressure', 'display_clipped_pressure', 'turbulent_diffusion', 'old_treatment_for_turbulent_diffusion']
    _child_classes = dict(
        schnerr_evap_coeff=schnerr_evap_coeff,
        schnerr_cond_coeff=schnerr_cond_coeff,
        max_vapor_pressure_ratio=max_vapor_pressure_ratio,
        min_vapor_pressure=min_vapor_pressure,
        display_clipped_pressure=display_clipped_pressure,
        turbulent_diffusion=turbulent_diffusion,
        old_treatment_for_turbulent_diffusion=old_treatment_for_turbulent_diffusion,
    )
    return_type = 'object'

class vof_from_min_limit(Real):
    """
    Minimum volume fraction below which mass transfer rate is set to zero.
    """
    _version = '222'
    fluent_name = 'vof-from-min-limit'
    _python_name = 'vof_from_min_limit'
    return_type = 'object'

class vof_from_max_limit(Real):
    """
    Maximum volume fraction below which mass transfer rate is set to zero.
    """
    _version = '222'
    fluent_name = 'vof-from-max-limit'
    _python_name = 'vof_from_max_limit'
    return_type = 'object'

class vof_to_min_limit(Real):
    """
    Minimum volume fraction below which mass transfer rate is set to zero.
    """
    _version = '222'
    fluent_name = 'vof-to-min-limit'
    _python_name = 'vof_to_min_limit'
    return_type = 'object'

class vof_to_max_limit(Real):
    """
    Maximum volume fraction below which mass transfer rate is set to zero.
    """
    _version = '222'
    fluent_name = 'vof-to-max-limit'
    _python_name = 'vof_to_max_limit'
    return_type = 'object'

class ia_norm_min_limit(Real):
    """
    Minimum normalized area density below which mass transfer rate is set to zero.
    """
    _version = '222'
    fluent_name = 'ia-norm-min-limit'
    _python_name = 'ia_norm_min_limit'
    return_type = 'object'

class max_rel_humidity(Real):
    """
    Maximum value of relative humidity to limit condensation rate.
    """
    _version = '222'
    fluent_name = 'max-rel-humidity'
    _python_name = 'max_rel_humidity'
    return_type = 'object'

class evaporation_condensation(Group):
    """
    'evaporation_condensation' child.
    """
    _version = '222'
    fluent_name = 'evaporation-condensation'
    _python_name = 'evaporation_condensation'
    child_names = ['vof_from_min_limit', 'vof_from_max_limit', 'vof_to_min_limit', 'vof_to_max_limit', 'ia_norm_min_limit', 'max_rel_humidity']
    _child_classes = dict(
        vof_from_min_limit=vof_from_min_limit,
        vof_from_max_limit=vof_from_max_limit,
        vof_to_min_limit=vof_to_min_limit,
        vof_to_max_limit=vof_to_max_limit,
        ia_norm_min_limit=ia_norm_min_limit,
        max_rel_humidity=max_rel_humidity,
    )
    return_type = 'object'

class heat_flux_relaxation_factor(Real):
    """
    Under-relaxation factor for boiling heat flux.
    """
    _version = '222'
    fluent_name = 'heat-flux-relaxation-factor'
    _python_name = 'heat_flux_relaxation_factor'
    return_type = 'object'

class show_expert_options(Boolean):
    """
    Exposes expert options of min/max superheat along with wetting fraction controls.
    """
    _version = '222'
    fluent_name = 'show-expert-options?'
    _python_name = 'show_expert_options'
    return_type = 'object'

class two_resistance_boiling_framework(Boolean):
    """
    Allow generalized two-resistance framework for boiling model.
    """
    _version = '222'
    fluent_name = 'two-resistance-boiling-framework?'
    _python_name = 'two_resistance_boiling_framework'
    return_type = 'object'

class boiling(Group):
    """
    'boiling' child.
    """
    _version = '222'
    fluent_name = 'boiling'
    _python_name = 'boiling'
    child_names = ['heat_flux_relaxation_factor', 'show_expert_options', 'two_resistance_boiling_framework']
    _child_classes = dict(
        heat_flux_relaxation_factor=heat_flux_relaxation_factor,
        show_expert_options=show_expert_options,
        two_resistance_boiling_framework=two_resistance_boiling_framework,
    )
    return_type = 'object'

class vof_min_seeding(Real):
    """
    Minimum vof seeding for non-zero area density in heat and mass transfer.
    """
    _version = '222'
    fluent_name = 'vof-min-seeding'
    _python_name = 'vof_min_seeding'
    return_type = 'object'

class ia_grad_sym(Boolean):
    """
    Interfacial area density gradient-symmetric mechanism.
    """
    _version = '222'
    fluent_name = 'ia-grad-sym?'
    _python_name = 'ia_grad_sym'
    return_type = 'object'

class area_density_1(Group):
    """
    'area_density' child.
    """
    _version = '222'
    fluent_name = 'area-density'
    _python_name = 'area_density'
    child_names = ['vof_min_seeding', 'ia_grad_sym']
    _child_classes = dict(
        vof_min_seeding=vof_min_seeding,
        ia_grad_sym=ia_grad_sym,
    )
    return_type = 'object'

class alternative_energy_treatment(Boolean):
    """
    Alternative treatment of latent heat source due to mass transfer.
    """
    _version = '222'
    fluent_name = 'alternative-energy-treatment?'
    _python_name = 'alternative_energy_treatment'
    return_type = 'object'

class heat_mass_transfer(Group):
    """
    'heat_mass_transfer' child.
    """
    _version = '222'
    fluent_name = 'heat-mass-transfer'
    _python_name = 'heat_mass_transfer'
    child_names = ['cavitation', 'evaporation_condensation', 'boiling', 'area_density', 'alternative_energy_treatment']
    _child_classes = dict(
        cavitation=cavitation,
        evaporation_condensation=evaporation_condensation,
        boiling=boiling,
        area_density=area_density_1,
        alternative_energy_treatment=alternative_energy_treatment,
    )
    return_type = 'object'

class smoothed_density_stabilization_method(Boolean):
    """
    Enable/disable smoothed density for momentum stabilization.
    """
    _version = '222'
    fluent_name = 'smoothed-density-stabilization-method?'
    _python_name = 'smoothed_density_stabilization_method'
    return_type = 'object'

class num_of_density_smoothing(Integer):
    """
    Number of density smoothings.
    """
    _version = '222'
    fluent_name = 'num-of-density-smoothing'
    _python_name = 'num_of_density_smoothing'
    return_type = 'object'

class false_time_step_linearization(Boolean):
    """
    False time-step linearization for added stability.
    """
    _version = '222'
    fluent_name = 'false-time-step-linearization?'
    _python_name = 'false_time_step_linearization'
    return_type = 'object'

class enable_1(Boolean):
    """
    Enable advanced automatic time stepping for better stability.
    """
    _version = '222'
    fluent_name = 'enable?'
    _python_name = 'enable'
    return_type = 'object'

class dt_init_limit(Real):
    """
    Maximum value for pseudo time step size during first iteration.
    """
    _version = '222'
    fluent_name = 'dt-init-limit'
    _python_name = 'dt_init_limit'
    return_type = 'object'

class dt_max(Real):
    """
    Maximum pseudo time step size.
    """
    _version = '222'
    fluent_name = 'dt-max'
    _python_name = 'dt_max'
    return_type = 'object'

class dt_factor_min(Real):
    """
    Minimum time step size change factor.
    """
    _version = '222'
    fluent_name = 'dt-factor-min'
    _python_name = 'dt_factor_min'
    return_type = 'object'

class dt_factor_max(Real):
    """
    Maximum time step size change factor.
    """
    _version = '222'
    fluent_name = 'dt-factor-max'
    _python_name = 'dt_factor_max'
    return_type = 'object'

class max_velocity_ratio(Real):
    """
    Maximum to average velocity ratio to freeze the pseudo time-step size.
    """
    _version = '222'
    fluent_name = 'max-velocity-ratio'
    _python_name = 'max_velocity_ratio'
    return_type = 'object'

class auto_dt_advanced_controls(Group):
    """
    'auto_dt_advanced_controls' child.
    """
    _version = '222'
    fluent_name = 'auto-dt-advanced-controls'
    _python_name = 'auto_dt_advanced_controls'
    child_names = ['enable', 'dt_init_limit', 'dt_max', 'dt_factor_min', 'dt_factor_max', 'max_velocity_ratio']
    _child_classes = dict(
        enable=enable_1,
        dt_init_limit=dt_init_limit,
        dt_max=dt_max,
        dt_factor_min=dt_factor_min,
        dt_factor_max=dt_factor_max,
        max_velocity_ratio=max_velocity_ratio,
    )
    return_type = 'object'

class pseudo_transient(Group):
    """
    'pseudo_transient' child.
    """
    _version = '222'
    fluent_name = 'pseudo-transient'
    _python_name = 'pseudo_transient'
    child_names = ['smoothed_density_stabilization_method', 'num_of_density_smoothing', 'false_time_step_linearization', 'auto_dt_advanced_controls']
    _child_classes = dict(
        smoothed_density_stabilization_method=smoothed_density_stabilization_method,
        num_of_density_smoothing=num_of_density_smoothing,
        false_time_step_linearization=false_time_step_linearization,
        auto_dt_advanced_controls=auto_dt_advanced_controls,
    )
    return_type = 'object'

class buoyancy_force_linearization(Boolean):
    """
    Enable/disable linearized buoyancy force.
    """
    _version = '222'
    fluent_name = 'buoyancy-force-linearization?'
    _python_name = 'buoyancy_force_linearization'
    return_type = 'object'

class blended_treatment_for_buoyancy_forces(Boolean):
    """
    Enable/disable use of  blended treatment for buoyancy force.
    """
    _version = '222'
    fluent_name = 'blended-treatment-for-buoyancy-forces?'
    _python_name = 'blended_treatment_for_buoyancy_forces'
    return_type = 'object'

class coupled_vof(Group):
    """
    'coupled_vof' child.
    """
    _version = '222'
    fluent_name = 'coupled-vof'
    _python_name = 'coupled_vof'
    child_names = ['buoyancy_force_linearization', 'blended_treatment_for_buoyancy_forces']
    _child_classes = dict(
        buoyancy_force_linearization=buoyancy_force_linearization,
        blended_treatment_for_buoyancy_forces=blended_treatment_for_buoyancy_forces,
    )
    return_type = 'object'

class low_order_rhie_chow(Boolean):
    """
    Use low order velocity interpolation in flux calculation.
    """
    _version = '222'
    fluent_name = 'low-order-rhie-chow?'
    _python_name = 'low_order_rhie_chow'
    return_type = 'object'

class rhie_chow_flux(Group):
    """
    'rhie_chow_flux' child.
    """
    _version = '222'
    fluent_name = 'rhie-chow-flux'
    _python_name = 'rhie_chow_flux'
    child_names = ['low_order_rhie_chow']
    _child_classes = dict(
        low_order_rhie_chow=low_order_rhie_chow,
    )
    return_type = 'object'

class limit_pressure_correction_gradient(Boolean):
    """
    Use limited pressure correction gradient in skewness corrections for better stability.
    """
    _version = '222'
    fluent_name = 'limit-pressure-correction-gradient?'
    _python_name = 'limit_pressure_correction_gradient'
    return_type = 'object'

class skewness_correction(Group):
    """
    'skewness_correction' child.
    """
    _version = '222'
    fluent_name = 'skewness-correction'
    _python_name = 'skewness_correction'
    child_names = ['limit_pressure_correction_gradient']
    _child_classes = dict(
        limit_pressure_correction_gradient=limit_pressure_correction_gradient,
    )
    return_type = 'object'

class p_v_coupling_1(Group):
    """
    'p_v_coupling' child.
    """
    _version = '222'
    fluent_name = 'p-v-coupling'
    _python_name = 'p_v_coupling'
    child_names = ['coupled_vof', 'rhie_chow_flux', 'skewness_correction']
    _child_classes = dict(
        coupled_vof=coupled_vof,
        rhie_chow_flux=rhie_chow_flux,
        skewness_correction=skewness_correction,
    )
    return_type = 'object'

class outer_iterations(Integer):
    """
    Number of outer iterations in hybrid nita.
    """
    _version = '222'
    fluent_name = 'outer-iterations'
    _python_name = 'outer_iterations'
    return_type = 'object'

class initial_time_steps(Integer):
    """
    Number of initial time-steps.
    """
    _version = '222'
    fluent_name = 'initial-time-steps'
    _python_name = 'initial_time_steps'
    return_type = 'object'

class initial_outer_iter(Integer):
    """
    Number of initial outer iterations.
    """
    _version = '222'
    fluent_name = 'initial-outer-iter'
    _python_name = 'initial_outer_iter'
    return_type = 'object'

class initial_outer_iterations(Group):
    """
    'initial_outer_iterations' child.
    """
    _version = '222'
    fluent_name = 'initial-outer-iterations'
    _python_name = 'initial_outer_iterations'
    child_names = ['initial_time_steps', 'initial_outer_iter']
    _child_classes = dict(
        initial_time_steps=initial_time_steps,
        initial_outer_iter=initial_outer_iter,
    )
    return_type = 'object'

class enable_instability_detector(Boolean):
    """
    Enable instability detector for better stability.
    """
    _version = '222'
    fluent_name = 'enable-instability-detector?'
    _python_name = 'enable_instability_detector'
    return_type = 'object'

class set_cfl_limit(Real):
    """
    Courant Number limit for detection of unstable event.
    """
    _version = '222'
    fluent_name = 'set-cfl-limit'
    _python_name = 'set_cfl_limit'
    return_type = 'object'

class set_cfl_type(String, AllowedValuesMixin):
    """
    Courant Number type for detection of unstable event.
    """
    _version = '222'
    fluent_name = 'set-cfl-type'
    _python_name = 'set_cfl_type'
    return_type = 'object'

class set_velocity_limit(Real):
    """
    Velocity limit for detection of unstable event.
    """
    _version = '222'
    fluent_name = 'set-velocity-limit'
    _python_name = 'set_velocity_limit'
    return_type = 'object'

class unstable_event_outer_iterations(Integer):
    """
    Number of outer iterations for unstable event.
    """
    _version = '222'
    fluent_name = 'unstable-event-outer-iterations'
    _python_name = 'unstable_event_outer_iterations'
    return_type = 'object'

class instability_detector(Group):
    """
    'instability_detector' child.
    """
    _version = '222'
    fluent_name = 'instability-detector'
    _python_name = 'instability_detector'
    child_names = ['enable_instability_detector', 'set_cfl_limit', 'set_cfl_type', 'set_velocity_limit', 'unstable_event_outer_iterations']
    _child_classes = dict(
        enable_instability_detector=enable_instability_detector,
        set_cfl_limit=set_cfl_limit,
        set_cfl_type=set_cfl_type,
        set_velocity_limit=set_velocity_limit,
        unstable_event_outer_iterations=unstable_event_outer_iterations,
    )
    return_type = 'object'

class hybrid_nita(Group):
    """
    'hybrid_nita' child.
    """
    _version = '222'
    fluent_name = 'hybrid-nita'
    _python_name = 'hybrid_nita'
    child_names = ['outer_iterations', 'initial_outer_iterations', 'instability_detector']
    _child_classes = dict(
        outer_iterations=outer_iterations,
        initial_outer_iterations=initial_outer_iterations,
        instability_detector=instability_detector,
    )
    return_type = 'object'

class solve_flow_last(Boolean):
    """
    Solve flow equation at the end of iteration as an alternative.
    """
    _version = '222'
    fluent_name = 'solve-flow-last?'
    _python_name = 'solve_flow_last'
    return_type = 'object'

class solve_exp_vof_at_end(Boolean):
    """
    Solve Explicit VOF at the end of time-step as an alternative.
    """
    _version = '222'
    fluent_name = 'solve-exp-vof-at-end?'
    _python_name = 'solve_exp_vof_at_end'
    return_type = 'object'

class equation_order(Group):
    """
    'equation_order' child.
    """
    _version = '222'
    fluent_name = 'equation-order'
    _python_name = 'equation_order'
    child_names = ['solve_flow_last', 'solve_exp_vof_at_end']
    _child_classes = dict(
        solve_flow_last=solve_flow_last,
        solve_exp_vof_at_end=solve_exp_vof_at_end,
    )
    return_type = 'object'

class enable_dynamic_strength(Boolean):
    """
    Enable dynamic strength to reduce compression in the tangential direction to the interface.
    """
    _version = '222'
    fluent_name = 'enable-dynamic-strength?'
    _python_name = 'enable_dynamic_strength'
    return_type = 'object'

class set_dynamic_strength_exponent(Real):
    """
    Cosine exponent in dynamic strength treatment.
    """
    _version = '222'
    fluent_name = 'set-dynamic-strength-exponent'
    _python_name = 'set_dynamic_strength_exponent'
    return_type = 'object'

class set_maximum_dynamic_strength(Real):
    """
    Maximum value of dynamic anti-diffusion strength.
    """
    _version = '222'
    fluent_name = 'set-maximum-dynamic-strength'
    _python_name = 'set_maximum_dynamic_strength'
    return_type = 'object'

class anti_diffusion(Group):
    """
    'anti_diffusion' child.
    """
    _version = '222'
    fluent_name = 'anti-diffusion'
    _python_name = 'anti_diffusion'
    child_names = ['enable_dynamic_strength', 'set_dynamic_strength_exponent', 'set_maximum_dynamic_strength']
    _child_classes = dict(
        enable_dynamic_strength=enable_dynamic_strength,
        set_dynamic_strength_exponent=set_dynamic_strength_exponent,
        set_maximum_dynamic_strength=set_maximum_dynamic_strength,
    )
    return_type = 'object'

class advanced_stability_controls(Group):
    """
    'advanced_stability_controls' child.
    """
    _version = '222'
    fluent_name = 'advanced-stability-controls'
    _python_name = 'advanced_stability_controls'
    child_names = ['pseudo_transient', 'p_v_coupling', 'hybrid_nita', 'equation_order', 'anti_diffusion']
    _child_classes = dict(
        pseudo_transient=pseudo_transient,
        p_v_coupling=p_v_coupling_1,
        hybrid_nita=hybrid_nita,
        equation_order=equation_order,
        anti_diffusion=anti_diffusion,
    )
    return_type = 'object'

class recommended_defaults_for_existing_cases(Boolean):
    """
    'recommended_defaults_for_existing_cases' child.
    """
    _version = '222'
    fluent_name = 'recommended-defaults-for-existing-cases'
    _python_name = 'recommended_defaults_for_existing_cases'
    return_type = 'object'

class old_default_of_operating_density_method(Boolean):
    """
    'old_default_of_operating_density_method' child.
    """
    _version = '222'
    fluent_name = 'old-default-of-operating-density-method'
    _python_name = 'old_default_of_operating_density_method'
    return_type = 'object'

class old_default_of_volume_fraction_smoothing(Boolean):
    """
    'old_default_of_volume_fraction_smoothing' child.
    """
    _version = '222'
    fluent_name = 'old-default-of-volume-fraction-smoothing'
    _python_name = 'old_default_of_volume_fraction_smoothing'
    return_type = 'object'

class old_variant_of_pesto_for_cases_using_structured_mesh(Boolean):
    """
    'old_variant_of_pesto_for_cases_using_structured_mesh' child.
    """
    _version = '222'
    fluent_name = 'old-variant-of-pesto-for-cases-using-structured-mesh'
    _python_name = 'old_variant_of_pesto_for_cases_using_structured_mesh'
    return_type = 'object'

class revert_to_pre_r20_1_default_settings(Group):
    """
    'revert_to_pre_r20_1_default_settings' child.
    """
    _version = '222'
    fluent_name = 'revert-to-pre-r20.1-default-settings?'
    _python_name = 'revert_to_pre_r20_1_default_settings'
    child_names = ['old_default_of_operating_density_method', 'old_default_of_volume_fraction_smoothing', 'old_variant_of_pesto_for_cases_using_structured_mesh']
    _child_classes = dict(
        old_default_of_operating_density_method=old_default_of_operating_density_method,
        old_default_of_volume_fraction_smoothing=old_default_of_volume_fraction_smoothing,
        old_variant_of_pesto_for_cases_using_structured_mesh=old_variant_of_pesto_for_cases_using_structured_mesh,
    )
    return_type = 'object'

class default_controls(Group):
    """
    'default_controls' child.
    """
    _version = '222'
    fluent_name = 'default-controls'
    _python_name = 'default_controls'
    child_names = ['recommended_defaults_for_existing_cases', 'revert_to_pre_r20_1_default_settings']
    _child_classes = dict(
        recommended_defaults_for_existing_cases=recommended_defaults_for_existing_cases,
        revert_to_pre_r20_1_default_settings=revert_to_pre_r20_1_default_settings,
    )
    return_type = 'object'

class pressure_corr_grad(Boolean):
    """
    Enable/disable pressure correction gradient limiting in corrector step.
    """
    _version = '222'
    fluent_name = 'pressure-corr-grad?'
    _python_name = 'pressure_corr_grad'
    return_type = 'object'

class face_pressure_calculation_method(String):
    """
    Face pressure calculation method for corrector step .
    """
    _version = '222'
    fluent_name = 'face-pressure-calculation-method'
    _python_name = 'face_pressure_calculation_method'
    return_type = 'object'

class exclude_transient_term_in_face_pressure_calc(Boolean):
    """
    Enable/disale transient terms in face pressure calculation.
    """
    _version = '222'
    fluent_name = 'exclude-transient-term-in-face-pressure-calc'
    _python_name = 'exclude_transient_term_in_face_pressure_calc'
    return_type = 'object'

class face_pressure_options(Group):
    """
    'face_pressure_options' child.
    """
    _version = '222'
    fluent_name = 'face-pressure-options'
    _python_name = 'face_pressure_options'
    child_names = ['pressure_corr_grad', 'face_pressure_calculation_method', 'exclude_transient_term_in_face_pressure_calc']
    _child_classes = dict(
        pressure_corr_grad=pressure_corr_grad,
        face_pressure_calculation_method=face_pressure_calculation_method,
        exclude_transient_term_in_face_pressure_calc=exclude_transient_term_in_face_pressure_calc,
    )
    return_type = 'object'

class face_pressure_controls(Group):
    """
    'face_pressure_controls' child.
    """
    _version = '222'
    fluent_name = 'face-pressure-controls'
    _python_name = 'face_pressure_controls'
    child_names = ['face_pressure_options']
    _child_classes = dict(
        face_pressure_options=face_pressure_options,
    )
    return_type = 'object'

class execute_settings_optimization(Boolean):
    """
    Enable/disable optimized settings.
    """
    _version = '222'
    fluent_name = 'execute-settings-optimization?'
    _python_name = 'execute_settings_optimization'
    return_type = 'object'

class execute_advanced_stabilization(Boolean):
    """
    Enable/disable advanced stabilization.
    """
    _version = '222'
    fluent_name = 'execute-advanced-stabilization?'
    _python_name = 'execute_advanced_stabilization'
    return_type = 'object'

class blended_compressive_scheme(Boolean):
    """
    Blended Compressive discretization scheme for VOF.
    """
    _version = '222'
    fluent_name = 'blended-compressive-scheme?'
    _python_name = 'blended_compressive_scheme'
    return_type = 'object'

class pseudo_transient_stabilization(Boolean):
    """
    Multiphase enhanced compressible flow numerics options.
    """
    _version = '222'
    fluent_name = 'pseudo-transient-stabilization?'
    _python_name = 'pseudo_transient_stabilization'
    return_type = 'object'

class additional_stabilization_controls(Group):
    """
    'additional_stabilization_controls' child.
    """
    _version = '222'
    fluent_name = 'additional-stabilization-controls'
    _python_name = 'additional_stabilization_controls'
    child_names = ['blended_compressive_scheme', 'pseudo_transient_stabilization']
    _child_classes = dict(
        blended_compressive_scheme=blended_compressive_scheme,
        pseudo_transient_stabilization=pseudo_transient_stabilization,
    )
    return_type = 'object'

class execute_additional_stability_controls(Integer):
    """
    Execute additional stability controls for VOF.
    """
    _version = '222'
    fluent_name = 'execute-additional-stability-controls?'
    _python_name = 'execute_additional_stability_controls'
    return_type = 'object'

class enable_velocity_limiting(Boolean):
    """
    Enable/disable velocity limiting treatment.
    """
    _version = '222'
    fluent_name = 'enable-velocity-limiting?'
    _python_name = 'enable_velocity_limiting'
    return_type = 'object'

class max_vol_mag(Real):
    """
    'max_vol_mag' child.
    """
    _version = '222'
    fluent_name = 'max-vol-mag'
    _python_name = 'max_vol_mag'
    return_type = 'object'

class vol_frac_cutoff(Real):
    """
    'vol_frac_cutoff' child.
    """
    _version = '222'
    fluent_name = 'vol-frac-cutoff'
    _python_name = 'vol_frac_cutoff'
    return_type = 'object'

class set_velocity_and_vof_cutoffs_child(Group):
    """
    'child_object_type' of set_velocity_and_vof_cutoffs.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'set_velocity_and_vof_cutoffs_child'
    child_names = ['max_vol_mag', 'vol_frac_cutoff']
    _child_classes = dict(
        max_vol_mag=max_vol_mag,
        vol_frac_cutoff=vol_frac_cutoff,
    )
    return_type = 'object'

class set_velocity_and_vof_cutoffs(NamedObject[set_velocity_and_vof_cutoffs_child], CreatableNamedObjectMixinOld[set_velocity_and_vof_cutoffs_child]):
    """
    'set_velocity_and_vof_cutoffs' child.
    """
    _version = '222'
    fluent_name = 'set-velocity-and-vof-cutoffs'
    _python_name = 'set_velocity_and_vof_cutoffs'
    child_object_type = set_velocity_and_vof_cutoffs_child
    return_type = 'object'

class set_damping_strengths_child(Real):
    """
    'child_object_type' of set_damping_strengths.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'set_damping_strengths_child'
    return_type = 'object'

class set_damping_strengths(NamedObject[set_damping_strengths_child], CreatableNamedObjectMixinOld[set_damping_strengths_child]):
    """
    'set_damping_strengths' child.
    """
    _version = '222'
    fluent_name = 'set-damping-strengths'
    _python_name = 'set_damping_strengths'
    child_object_type = set_damping_strengths_child
    return_type = 'object'

class set_velocity_cutoff(Real):
    """
    Max velocity magnitude.
    """
    _version = '222'
    fluent_name = 'set-velocity-cutoff'
    _python_name = 'set_velocity_cutoff'
    return_type = 'object'

class set_damping_strength(Real):
    """
    Damping Strength.
    """
    _version = '222'
    fluent_name = 'set-damping-strength'
    _python_name = 'set_damping_strength'
    return_type = 'object'

class verbosity_2(Boolean):
    """
    Enable verbosity to print number of velocity limited cells during iterations.
    """
    _version = '222'
    fluent_name = 'verbosity?'
    _python_name = 'verbosity'
    return_type = 'object'

class velocity_limiting_treatment(Group):
    """
    'velocity_limiting_treatment' child.
    """
    _version = '222'
    fluent_name = 'velocity-limiting-treatment'
    _python_name = 'velocity_limiting_treatment'
    child_names = ['enable_velocity_limiting', 'set_velocity_and_vof_cutoffs', 'set_damping_strengths', 'set_velocity_cutoff', 'set_damping_strength', 'verbosity']
    _child_classes = dict(
        enable_velocity_limiting=enable_velocity_limiting,
        set_velocity_and_vof_cutoffs=set_velocity_and_vof_cutoffs,
        set_damping_strengths=set_damping_strengths,
        set_velocity_cutoff=set_velocity_cutoff,
        set_damping_strength=set_damping_strength,
        verbosity=verbosity_2,
    )
    return_type = 'object'

class solution_stabilization_1(Group):
    """
    'solution_stabilization' child.
    """
    _version = '222'
    fluent_name = 'solution-stabilization'
    _python_name = 'solution_stabilization'
    child_names = ['execute_settings_optimization', 'execute_advanced_stabilization', 'additional_stabilization_controls', 'execute_additional_stability_controls', 'velocity_limiting_treatment']
    _child_classes = dict(
        execute_settings_optimization=execute_settings_optimization,
        execute_advanced_stabilization=execute_advanced_stabilization,
        additional_stabilization_controls=additional_stabilization_controls,
        execute_additional_stability_controls=execute_additional_stability_controls,
        velocity_limiting_treatment=velocity_limiting_treatment,
    )
    return_type = 'object'

class multiphase_numerics(Group):
    """
    The multiphase numerics options object.
    """
    _version = '222'
    fluent_name = 'multiphase-numerics'
    _python_name = 'multiphase_numerics'
    child_names = ['porous_media', 'compressible_flow', 'boiling_parameters', 'viscous_flow', 'heat_mass_transfer', 'advanced_stability_controls', 'default_controls', 'face_pressure_controls', 'solution_stabilization']
    _child_classes = dict(
        porous_media=porous_media,
        compressible_flow=compressible_flow,
        boiling_parameters=boiling_parameters,
        viscous_flow=viscous_flow,
        heat_mass_transfer=heat_mass_transfer,
        advanced_stability_controls=advanced_stability_controls,
        default_controls=default_controls,
        face_pressure_controls=face_pressure_controls,
        solution_stabilization=solution_stabilization_1,
    )
    return_type = 'object'

class nb_gradient(Boolean):
    """
    Enable/disable modified boundary treatment.
    """
    _version = '222'
    fluent_name = 'nb-gradient'
    _python_name = 'nb_gradient'
    return_type = 'object'

class boundary_treatment(Boolean):
    """
    Enable/disable modified/extended boundary treatment.
    """
    _version = '222'
    fluent_name = 'boundary-treatment'
    _python_name = 'boundary_treatment'
    return_type = 'object'

class extended_boundary_treatment(Boolean):
    """
    Enable/disable extended boundary treatment.
    """
    _version = '222'
    fluent_name = 'extended-boundary-treatment'
    _python_name = 'extended_boundary_treatment'
    return_type = 'object'

class nb_gradient_dbns(Group):
    """
    'nb_gradient_dbns' child.
    """
    _version = '222'
    fluent_name = 'nb-gradient-dbns'
    _python_name = 'nb_gradient_dbns'
    child_names = ['boundary_treatment', 'extended_boundary_treatment']
    _child_classes = dict(
        boundary_treatment=boundary_treatment,
        extended_boundary_treatment=extended_boundary_treatment,
    )
    return_type = 'object'

class nb_gradient_boundary_option(Group):
    """
    'nb_gradient_boundary_option' child.
    """
    _version = '222'
    fluent_name = 'nb-gradient-boundary-option?'
    _python_name = 'nb_gradient_boundary_option'
    child_names = ['nb_gradient', 'nb_gradient_dbns']
    _child_classes = dict(
        nb_gradient=nb_gradient,
        nb_gradient_dbns=nb_gradient_dbns,
    )
    return_type = 'object'

class set_verbosity(Integer):
    """
    Nita verbosity option.
    """
    _version = '222'
    fluent_name = 'set-verbosity'
    _python_name = 'set_verbosity'
    return_type = 'object'

class skewness_neighbor_coupling_1(Boolean):
    """
    Skewness neighbor coupling for nita.
    """
    _version = '222'
    fluent_name = 'skewness-neighbor-coupling'
    _python_name = 'skewness_neighbor_coupling'
    return_type = 'object'

class enable_2(Boolean):
    """
    Enable/disable hybrid nita settings.
    """
    _version = '222'
    fluent_name = 'enable?'
    _python_name = 'enable'
    return_type = 'object'

class options_3(String, AllowedValuesMixin):
    """
    Hybrid nita option.
    """
    _version = '222'
    fluent_name = 'options'
    _python_name = 'options'
    return_type = 'object'

class multi_phase_setting(Group):
    """
    'multi_phase_setting' child.
    """
    _version = '222'
    fluent_name = 'multi-phase-setting'
    _python_name = 'multi_phase_setting'
    child_names = ['enable', 'options']
    _child_classes = dict(
        enable=enable_2,
        options=options_3,
    )
    return_type = 'object'

class single_phase_setting(String, AllowedValuesMixin):
    """
    Hybrid nita option.
    """
    _version = '222'
    fluent_name = 'single-phase-setting'
    _python_name = 'single_phase_setting'
    return_type = 'object'

class hybrid_nita_settings(Group):
    """
    'hybrid_nita_settings' child.
    """
    _version = '222'
    fluent_name = 'hybrid-nita-settings'
    _python_name = 'hybrid_nita_settings'
    child_names = ['multi_phase_setting', 'single_phase_setting']
    _child_classes = dict(
        multi_phase_setting=multi_phase_setting,
        single_phase_setting=single_phase_setting,
    )
    return_type = 'object'

class nita_expert_controls(Group):
    """
    'nita_expert_controls' child.
    """
    _version = '222'
    fluent_name = 'nita-expert-controls'
    _python_name = 'nita_expert_controls'
    child_names = ['set_verbosity', 'skewness_neighbor_coupling', 'hybrid_nita_settings']
    _child_classes = dict(
        set_verbosity=set_verbosity,
        skewness_neighbor_coupling=skewness_neighbor_coupling_1,
        hybrid_nita_settings=hybrid_nita_settings,
    )
    return_type = 'object'

class noniterative_time_advance(Boolean):
    """
    Enable/disable Use of Noniterative Time Advancement Scheme.
    """
    _version = '222'
    fluent_name = 'noniterative-time-advance?'
    _python_name = 'noniterative_time_advance'
    return_type = 'object'

class high_order_pressure(Boolean):
    """
    High order pressure extrapolation at overset interface.
    """
    _version = '222'
    fluent_name = 'high-order-pressure?'
    _python_name = 'high_order_pressure'
    return_type = 'object'

class interpolation_method(String, AllowedValuesMixin):
    """
    The interpolation method for overset interface(s).
    """
    _version = '222'
    fluent_name = 'interpolation-method'
    _python_name = 'interpolation_method'
    return_type = 'object'

class orphan_cell_treatment(Boolean):
    """
    Enable solver to run with orphans present.
    """
    _version = '222'
    fluent_name = 'orphan-cell-treatment?'
    _python_name = 'orphan_cell_treatment'
    return_type = 'object'

class mass_flux_correction_method(String, AllowedValuesMixin):
    """
    Mass flux correction option at overset interfaces.
    """
    _version = '222'
    fluent_name = 'mass-flux-correction-method'
    _python_name = 'mass_flux_correction_method'
    return_type = 'object'

class hybrid_mode_selection(String, AllowedValuesMixin):
    """
    Mode for hybrid interpolation.
    """
    _version = '222'
    fluent_name = 'hybrid-mode-selection'
    _python_name = 'hybrid_mode_selection'
    return_type = 'object'

class expert_3(Group):
    """
    'expert' child.
    """
    _version = '222'
    fluent_name = 'expert'
    _python_name = 'expert'
    child_names = ['mass_flux_correction_method', 'hybrid_mode_selection']
    _child_classes = dict(
        mass_flux_correction_method=mass_flux_correction_method,
        hybrid_mode_selection=hybrid_mode_selection,
    )
    return_type = 'object'

class overset_1(Group):
    """
    'overset' child.
    """
    _version = '222'
    fluent_name = 'overset'
    _python_name = 'overset'
    child_names = ['high_order_pressure', 'interpolation_method', 'orphan_cell_treatment', 'expert']
    _child_classes = dict(
        high_order_pressure=high_order_pressure,
        interpolation_method=interpolation_method,
        orphan_cell_treatment=orphan_cell_treatment,
        expert=expert_3,
    )
    return_type = 'object'

class flow_scheme(String, AllowedValuesMixin):
    """
    'flow_scheme' child.
    """
    _version = '222'
    fluent_name = 'flow-scheme'
    _python_name = 'flow_scheme'
    return_type = 'object'

class coupled_form(Boolean):
    """
    'coupled_form' child.
    """
    _version = '222'
    fluent_name = 'coupled-form'
    _python_name = 'coupled_form'
    return_type = 'object'

class solve_n_phase(Boolean):
    """
    Enable/disable N-Phase Volume Fraction equations.
    """
    _version = '222'
    fluent_name = 'solve-n-phase?'
    _python_name = 'solve_n_phase'
    return_type = 'object'

class p_v_coupling(Group):
    """
    'p_v_coupling' child.
    """
    _version = '222'
    fluent_name = 'p-v-coupling'
    _python_name = 'p_v_coupling'
    child_names = ['flow_scheme', 'coupled_form', 'solve_n_phase']
    _child_classes = dict(
        flow_scheme=flow_scheme,
        coupled_form=coupled_form,
        solve_n_phase=solve_n_phase,
    )
    return_type = 'object'

class phase_based_vof_discretization_child(Real):
    """
    'child_object_type' of phase_based_vof_discretization.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'phase_based_vof_discretization_child'
    return_type = 'object'

class phase_based_vof_discretization(NamedObject[phase_based_vof_discretization_child], CreatableNamedObjectMixinOld[phase_based_vof_discretization_child]):
    """
    'phase_based_vof_discretization' child.
    """
    _version = '222'
    fluent_name = 'phase-based-vof-discretization'
    _python_name = 'phase_based_vof_discretization'
    child_object_type = phase_based_vof_discretization_child
    return_type = 'object'

class reduced_rank_extrapolation(Boolean):
    """
    Enable/disable Reduced Rank Extrapolation method to accelerate solution time.
    """
    _version = '222'
    fluent_name = 'reduced-rank-extrapolation'
    _python_name = 'reduced_rank_extrapolation'
    return_type = 'object'

class subspace_size(Integer):
    """
    Subspace size.
    """
    _version = '222'
    fluent_name = 'subspace-size'
    _python_name = 'subspace_size'
    return_type = 'object'

class skip_itr(Integer):
    """
    Skip every n iterations.
    """
    _version = '222'
    fluent_name = 'skip-itr'
    _python_name = 'skip_itr'
    return_type = 'object'

class reduced_rank_extrapolation_options(Group):
    """
    'reduced_rank_extrapolation_options' child.
    """
    _version = '222'
    fluent_name = 'reduced-rank-extrapolation-options'
    _python_name = 'reduced_rank_extrapolation_options'
    child_names = ['subspace_size', 'skip_itr']
    _child_classes = dict(
        subspace_size=subspace_size,
        skip_itr=skip_itr,
    )
    return_type = 'object'

class residual_smoothing_factor(Real):
    """
    Residual smoothing factor.
    """
    _version = '222'
    fluent_name = 'residual-smoothing-factor'
    _python_name = 'residual_smoothing_factor'
    return_type = 'object'

class residual_smoothing_iteration(Integer):
    """
    Number of implicit iterations.
    """
    _version = '222'
    fluent_name = 'residual-smoothing-iteration'
    _python_name = 'residual_smoothing_iteration'
    return_type = 'object'

class residual_smoothing(Group):
    """
    'residual_smoothing' child.
    """
    _version = '222'
    fluent_name = 'residual-smoothing'
    _python_name = 'residual_smoothing'
    child_names = ['residual_smoothing_factor', 'residual_smoothing_iteration']
    _child_classes = dict(
        residual_smoothing_factor=residual_smoothing_factor,
        residual_smoothing_iteration=residual_smoothing_iteration,
    )
    return_type = 'object'

class unsteady_1st_order(Boolean):
    """
    Enable/disable first-order unsteady solution model.
    """
    _version = '222'
    fluent_name = 'unsteady-1st-order?'
    _python_name = 'unsteady_1st_order'
    return_type = 'object'

class unsteady_2nd_order(Boolean):
    """
    Enable/disable second-order unsteady solution model.
    """
    _version = '222'
    fluent_name = 'unsteady-2nd-order?'
    _python_name = 'unsteady_2nd_order'
    return_type = 'object'

class unsteady_2nd_order_bounded(Boolean):
    """
    Enable/disable bounded second-order unsteady formulation.
    """
    _version = '222'
    fluent_name = 'unsteady-2nd-order-bounded?'
    _python_name = 'unsteady_2nd_order_bounded'
    return_type = 'object'

class unsteady_global_time(Boolean):
    """
    Enable/disable unsteady global-time-step solution model.
    """
    _version = '222'
    fluent_name = 'unsteady-global-time?'
    _python_name = 'unsteady_global_time'
    return_type = 'object'

class high_order_rc(Boolean):
    """
    Use low order velocity interpolation in flux calculation.
    """
    _version = '222'
    fluent_name = 'high-order-rc?'
    _python_name = 'high_order_rc'
    return_type = 'object'

class high_order_rc_hybrid_treatment(Boolean):
    """
    Enable/disable use of hybrid treatment for high order Rhie-Chow flux.
    """
    _version = '222'
    fluent_name = 'high-order-rc-hybrid-treatment?'
    _python_name = 'high_order_rc_hybrid_treatment'
    return_type = 'object'

class force_treatment_of_unsteady_rc(Boolean):
    """
    Enable/disable use of forced treatment of unsteady terms in Rhie-Chow flux.
    """
    _version = '222'
    fluent_name = 'force-treatment-of-unsteady-rc?'
    _python_name = 'force_treatment_of_unsteady_rc'
    return_type = 'object'

class unstructured_var_presto_scheme(Boolean):
    """
    Enable/disable use of unstructured variant of PRESTO pressure scheme.
    """
    _version = '222'
    fluent_name = 'unstructured-var-presto-scheme?'
    _python_name = 'unstructured_var_presto_scheme'
    return_type = 'object'

class new_framework_for_vof_specific_node_based_treatment(Boolean):
    """
    Enable/disable new framework for vof specific node based treatments.
    """
    _version = '222'
    fluent_name = 'new-framework-for-vof-specific-node-based-treatment?'
    _python_name = 'new_framework_for_vof_specific_node_based_treatment'
    return_type = 'object'

class vof_numerics(Group):
    """
    'vof_numerics' child.
    """
    _version = '222'
    fluent_name = 'vof-numerics'
    _python_name = 'vof_numerics'
    child_names = ['high_order_rc', 'high_order_rc_hybrid_treatment', 'force_treatment_of_unsteady_rc', 'unstructured_var_presto_scheme', 'new_framework_for_vof_specific_node_based_treatment']
    _child_classes = dict(
        high_order_rc=high_order_rc,
        high_order_rc_hybrid_treatment=high_order_rc_hybrid_treatment,
        force_treatment_of_unsteady_rc=force_treatment_of_unsteady_rc,
        unstructured_var_presto_scheme=unstructured_var_presto_scheme,
        new_framework_for_vof_specific_node_based_treatment=new_framework_for_vof_specific_node_based_treatment,
    )
    return_type = 'object'

class enable_fast_mode(Boolean):
    """
    Enable/disable use of fast mode.
    """
    _version = '222'
    fluent_name = 'enable-fast-mode'
    _python_name = 'enable_fast_mode'
    return_type = 'object'

class enable_memory_saving_mode(Boolean):
    """
    Enable/disable use of Memory Saving Mode.
    """
    _version = '222'
    fluent_name = 'enable-memory-saving-mode'
    _python_name = 'enable_memory_saving_mode'
    return_type = 'object'

class disable_warped_face_gradient_correction(Command):
    """
    'disable_warped_face_gradient_correction' command.
    """
    _version = '222'
    fluent_name = 'disable-warped-face-gradient-correction'
    _python_name = 'disable_warped_face_gradient_correction'
    return_type = 'object'

class enable_3(Group):
    """
    'enable' child.
    """
    _version = '222'
    fluent_name = 'enable?'
    _python_name = 'enable'
    child_names = ['enable_fast_mode', 'enable_memory_saving_mode']
    command_names = ['disable_warped_face_gradient_correction']
    _child_classes = dict(
        enable_fast_mode=enable_fast_mode,
        enable_memory_saving_mode=enable_memory_saving_mode,
        disable_warped_face_gradient_correction=disable_warped_face_gradient_correction,
    )
    return_type = 'object'

class turbulence_options(String, AllowedValuesMixin):
    """
    Options:
     Legacy computations 
     New computations .
    """
    _version = '222'
    fluent_name = 'turbulence-options'
    _python_name = 'turbulence_options'
    return_type = 'object'

class warped_face_gradient_correction(Group):
    """
    'warped_face_gradient_correction' child.
    """
    _version = '222'
    fluent_name = 'warped-face-gradient-correction'
    _python_name = 'warped_face_gradient_correction'
    child_names = ['enable', 'turbulence_options']
    _child_classes = dict(
        enable=enable_3,
        turbulence_options=turbulence_options,
    )
    return_type = 'object'

class coupled_solver(String, AllowedValuesMixin):
    """
    Pseudo time step size formulation for the pseudo time method.
    """
    _version = '222'
    fluent_name = 'coupled-solver'
    _python_name = 'coupled_solver'
    return_type = 'object'

class segregated_solver(String, AllowedValuesMixin):
    """
    Pseudo time step size formulation for the pseudo time method.
    """
    _version = '222'
    fluent_name = 'segregated-solver'
    _python_name = 'segregated_solver'
    return_type = 'object'

class density_based_solver(String, AllowedValuesMixin):
    """
    Pseudo time step size formulation for the pseudo time method.
    """
    _version = '222'
    fluent_name = 'density-based-solver'
    _python_name = 'density_based_solver'
    return_type = 'object'

class formulation(Group):
    """
    'formulation' child.
    """
    _version = '222'
    fluent_name = 'formulation'
    _python_name = 'formulation'
    child_names = ['coupled_solver', 'segregated_solver', 'density_based_solver']
    _child_classes = dict(
        coupled_solver=coupled_solver,
        segregated_solver=segregated_solver,
        density_based_solver=density_based_solver,
    )
    return_type = 'object'

class pseudo_time_courant_number(Real):
    """
    Courant number for the local pseudo time method.
    """
    _version = '222'
    fluent_name = 'pseudo-time-courant-number'
    _python_name = 'pseudo_time_courant_number'
    return_type = 'object'

class pseudo_time_step_method_solid_zone(Boolean):
    """
    Enable/disable pseudo time step method for solid zones.
    """
    _version = '222'
    fluent_name = 'pseudo-time-step-method-solid-zone?'
    _python_name = 'pseudo_time_step_method_solid_zone'
    return_type = 'object'

class time_step_size_scale_factor(Real):
    """
    Time step size scale factor for solid zones.
    """
    _version = '222'
    fluent_name = 'time-step-size-scale-factor'
    _python_name = 'time_step_size_scale_factor'
    return_type = 'object'

class local_time_step_settings(Group):
    """
    'local_time_step_settings' child.
    """
    _version = '222'
    fluent_name = 'local-time-step-settings'
    _python_name = 'local_time_step_settings'
    child_names = ['pseudo_time_courant_number', 'pseudo_time_step_method_solid_zone', 'time_step_size_scale_factor']
    _child_classes = dict(
        pseudo_time_courant_number=pseudo_time_courant_number,
        pseudo_time_step_method_solid_zone=pseudo_time_step_method_solid_zone,
        time_step_size_scale_factor=time_step_size_scale_factor,
    )
    return_type = 'object'

class auto_time_step_size_cal(Boolean):
    """
    Enable/disable use of automatic time step size calculation.
    """
    _version = '222'
    fluent_name = 'auto-time-step-size-cal?'
    _python_name = 'auto_time_step_size_cal'
    return_type = 'object'

class pseudo_time_step_size(Real):
    """
    Pseudo time step size.
    """
    _version = '222'
    fluent_name = 'pseudo-time-step-size'
    _python_name = 'pseudo_time_step_size'
    return_type = 'object'

class options_length_scale_calc_methods(String, AllowedValuesMixin):
    """
    Length Scale Calculation Method.
    """
    _version = '222'
    fluent_name = 'options-length-scale-calc-methods'
    _python_name = 'options_length_scale_calc_methods'
    return_type = 'object'

class auto_time_step_size_scale_factor(Real):
    """
    Auto Time Step Size Scaling Factor.
    """
    _version = '222'
    fluent_name = 'auto-time-step-size-scale-factor'
    _python_name = 'auto_time_step_size_scale_factor'
    return_type = 'object'

class length_scale(Real):
    """
    'length_scale' child.
    """
    _version = '222'
    fluent_name = 'length-scale'
    _python_name = 'length_scale'
    return_type = 'object'

class auto_time_size_calc_solid_zone(Boolean):
    """
    Enable/disable automatic time step size calculation for solid zone.
    """
    _version = '222'
    fluent_name = 'auto-time-size-calc-solid-zone?'
    _python_name = 'auto_time_size_calc_solid_zone'
    return_type = 'object'

class auto_time_solid_scale_factor(Real):
    """
    Auto Time Step Size Scaling Factor for solid zones.
    """
    _version = '222'
    fluent_name = 'auto-time-solid-scale-factor'
    _python_name = 'auto_time_solid_scale_factor'
    return_type = 'object'

class time_step_size_for_solid_zone(Real):
    """
    Pseudo Time Step Size for solid zones.
    """
    _version = '222'
    fluent_name = 'time-step-size-for-solid-zone'
    _python_name = 'time_step_size_for_solid_zone'
    return_type = 'object'

class global_time_step_settings(Group):
    """
    'global_time_step_settings' child.
    """
    _version = '222'
    fluent_name = 'global-time-step-settings'
    _python_name = 'global_time_step_settings'
    child_names = ['auto_time_step_size_cal', 'pseudo_time_step_size', 'options_length_scale_calc_methods', 'auto_time_step_size_scale_factor', 'length_scale', 'auto_time_size_calc_solid_zone', 'auto_time_solid_scale_factor', 'time_step_size_for_solid_zone']
    _child_classes = dict(
        auto_time_step_size_cal=auto_time_step_size_cal,
        pseudo_time_step_size=pseudo_time_step_size,
        options_length_scale_calc_methods=options_length_scale_calc_methods,
        auto_time_step_size_scale_factor=auto_time_step_size_scale_factor,
        length_scale=length_scale,
        auto_time_size_calc_solid_zone=auto_time_size_calc_solid_zone,
        auto_time_solid_scale_factor=auto_time_solid_scale_factor,
        time_step_size_for_solid_zone=time_step_size_for_solid_zone,
    )
    return_type = 'object'

class enable_pseudo_time_method(Boolean):
    """
    'enable_pseudo_time_method' child.
    """
    _version = '222'
    fluent_name = 'enable-pseudo-time-method?'
    _python_name = 'enable_pseudo_time_method'
    return_type = 'object'

class pseudo_time_scale_factor(Real):
    """
    'pseudo_time_scale_factor' child.
    """
    _version = '222'
    fluent_name = 'pseudo-time-scale-factor'
    _python_name = 'pseudo_time_scale_factor'
    return_type = 'object'

class implicit_under_relaxation_factor(Real):
    """
    'implicit_under_relaxation_factor' child.
    """
    _version = '222'
    fluent_name = 'implicit-under-relaxation-factor'
    _python_name = 'implicit_under_relaxation_factor'
    return_type = 'object'

class local_dt_child(Group):
    """
    'child_object_type' of local_dt.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'local_dt_child'
    child_names = ['enable_pseudo_time_method', 'pseudo_time_scale_factor', 'implicit_under_relaxation_factor']
    _child_classes = dict(
        enable_pseudo_time_method=enable_pseudo_time_method,
        pseudo_time_scale_factor=pseudo_time_scale_factor,
        implicit_under_relaxation_factor=implicit_under_relaxation_factor,
    )
    return_type = 'object'

class local_dt(NamedObject[local_dt_child], CreatableNamedObjectMixinOld[local_dt_child]):
    """
    'local_dt' child.
    """
    _version = '222'
    fluent_name = 'local-dt'
    _python_name = 'local_dt'
    child_object_type = local_dt_child
    return_type = 'object'

class global_dt_child(Group):
    """
    'child_object_type' of global_dt.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'global_dt_child'
    child_names = ['enable_pseudo_time_method', 'pseudo_time_scale_factor', 'implicit_under_relaxation_factor']
    _child_classes = dict(
        enable_pseudo_time_method=enable_pseudo_time_method,
        pseudo_time_scale_factor=pseudo_time_scale_factor,
        implicit_under_relaxation_factor=implicit_under_relaxation_factor,
    )
    return_type = 'object'

class global_dt(NamedObject[global_dt_child], CreatableNamedObjectMixinOld[global_dt_child]):
    """
    'global_dt' child.
    """
    _version = '222'
    fluent_name = 'global-dt'
    _python_name = 'global_dt'
    child_object_type = global_dt_child
    return_type = 'object'

class advanced_options(Group):
    """
    'advanced_options' child.
    """
    _version = '222'
    fluent_name = 'advanced-options'
    _python_name = 'advanced_options'
    child_names = ['local_dt', 'global_dt']
    _child_classes = dict(
        local_dt=local_dt,
        global_dt=global_dt,
    )
    return_type = 'object'

class local_dt_dualts_relax_child(Real):
    """
    'child_object_type' of local_dt_dualts_relax.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'local_dt_dualts_relax_child'
    return_type = 'object'

class local_dt_dualts_relax(NamedObject[local_dt_dualts_relax_child], CreatableNamedObjectMixinOld[local_dt_dualts_relax_child]):
    """
    'local_dt_dualts_relax' child.
    """
    _version = '222'
    fluent_name = 'local-dt-dualts-relax'
    _python_name = 'local_dt_dualts_relax'
    child_object_type = local_dt_dualts_relax_child
    return_type = 'object'

class global_dt_pseudo_relax_child(Real):
    """
    'child_object_type' of global_dt_pseudo_relax.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'global_dt_pseudo_relax_child'
    return_type = 'object'

class global_dt_pseudo_relax(NamedObject[global_dt_pseudo_relax_child], CreatableNamedObjectMixinOld[global_dt_pseudo_relax_child]):
    """
    'global_dt_pseudo_relax' child.
    """
    _version = '222'
    fluent_name = 'global-dt-pseudo-relax'
    _python_name = 'global_dt_pseudo_relax'
    child_object_type = global_dt_pseudo_relax_child
    return_type = 'object'

class relaxation_factors(Group):
    """
    'relaxation_factors' child.
    """
    _version = '222'
    fluent_name = 'relaxation-factors'
    _python_name = 'relaxation_factors'
    child_names = ['local_dt_dualts_relax', 'global_dt_pseudo_relax']
    _child_classes = dict(
        local_dt_dualts_relax=local_dt_dualts_relax,
        global_dt_pseudo_relax=global_dt_pseudo_relax,
    )
    return_type = 'object'

class verbosity_3(Integer):
    """
    'verbosity' child.
    """
    _version = '222'
    fluent_name = 'verbosity'
    _python_name = 'verbosity'
    return_type = 'object'

class pseudo_time_method(Group):
    """
    'pseudo_time_method' child.
    """
    _version = '222'
    fluent_name = 'pseudo-time-method'
    _python_name = 'pseudo_time_method'
    child_names = ['formulation', 'local_time_step_settings', 'global_time_step_settings', 'advanced_options', 'relaxation_factors', 'verbosity']
    _child_classes = dict(
        formulation=formulation,
        local_time_step_settings=local_time_step_settings,
        global_time_step_settings=global_time_step_settings,
        advanced_options=advanced_options,
        relaxation_factors=relaxation_factors,
        verbosity=verbosity_3,
    )
    return_type = 'object'

class set_solution_methods_to_default(Command):
    """
    'set_solution_methods_to_default' command.
    """
    _version = '222'
    fluent_name = 'set-solution-methods-to-default'
    _python_name = 'set_solution_methods_to_default'
    return_type = 'object'

class methods(Group):
    """
    'methods' child.
    """
    _version = '222'
    fluent_name = 'methods'
    _python_name = 'methods'
    child_names = ['accelerated_non_iterative_time_marching', 'convergence_acceleration_for_stretched_meshes', 'discretization_scheme', 'expert', 'flux_type', 'frozen_flux', 'gradient_scheme', 'high_order_term_relaxation', 'multiphase_numerics', 'nb_gradient_boundary_option', 'nita_expert_controls', 'noniterative_time_advance', 'overset', 'p_v_coupling', 'phase_based_vof_discretization', 'reduced_rank_extrapolation', 'reduced_rank_extrapolation_options', 'residual_smoothing', 'unsteady_1st_order', 'unsteady_2nd_order', 'unsteady_2nd_order_bounded', 'unsteady_global_time', 'vof_numerics', 'warped_face_gradient_correction', 'pseudo_time_method']
    command_names = ['set_solution_methods_to_default']
    _child_classes = dict(
        accelerated_non_iterative_time_marching=accelerated_non_iterative_time_marching,
        convergence_acceleration_for_stretched_meshes=convergence_acceleration_for_stretched_meshes,
        discretization_scheme=discretization_scheme,
        expert=expert_2,
        flux_type=flux_type,
        frozen_flux=frozen_flux,
        gradient_scheme=gradient_scheme,
        high_order_term_relaxation=high_order_term_relaxation,
        multiphase_numerics=multiphase_numerics,
        nb_gradient_boundary_option=nb_gradient_boundary_option,
        nita_expert_controls=nita_expert_controls,
        noniterative_time_advance=noniterative_time_advance,
        overset=overset_1,
        p_v_coupling=p_v_coupling,
        phase_based_vof_discretization=phase_based_vof_discretization,
        reduced_rank_extrapolation=reduced_rank_extrapolation,
        reduced_rank_extrapolation_options=reduced_rank_extrapolation_options,
        residual_smoothing=residual_smoothing,
        unsteady_1st_order=unsteady_1st_order,
        unsteady_2nd_order=unsteady_2nd_order,
        unsteady_2nd_order_bounded=unsteady_2nd_order_bounded,
        unsteady_global_time=unsteady_global_time,
        vof_numerics=vof_numerics,
        warped_face_gradient_correction=warped_face_gradient_correction,
        pseudo_time_method=pseudo_time_method,
        set_solution_methods_to_default=set_solution_methods_to_default,
    )
    return_type = 'object'

class zone_ids(StringList, AllowedValuesMixin):
    """
    'zone_ids' child.
    """
    _version = '222'
    fluent_name = 'zone-ids'
    _python_name = 'zone_ids'
    return_type = 'object'

class retain_instantaneous_values(Boolean):
    """
    'retain_instantaneous_values' child.
    """
    _version = '222'
    fluent_name = 'retain-instantaneous-values?'
    _python_name = 'retain_instantaneous_values'
    return_type = 'object'

class old_props(StringList, AllowedValuesMixin):
    """
    'old_props' child.
    """
    _version = '222'
    fluent_name = 'old-props'
    _python_name = 'old_props'
    return_type = 'object'

class zone_names(StringList, AllowedValuesMixin):
    """
    'zone_names' child.
    """
    _version = '222'
    fluent_name = 'zone-names'
    _python_name = 'zone_names'
    return_type = 'object'

class average_over(Integer):
    """
    'average_over' child.
    """
    _version = '222'
    fluent_name = 'average-over'
    _python_name = 'average_over'
    return_type = 'object'

class per_zone(Boolean):
    """
    'per_zone' child.
    """
    _version = '222'
    fluent_name = 'per-zone?'
    _python_name = 'per_zone'
    return_type = 'object'

class mesh_child(Group):
    """
    'child_object_type' of mesh.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'mesh_child'
    child_names = ['zone_ids', 'retain_instantaneous_values', 'old_props', 'zone_names', 'zone_list', 'average_over', 'per_zone']
    _child_classes = dict(
        zone_ids=zone_ids,
        retain_instantaneous_values=retain_instantaneous_values,
        old_props=old_props,
        zone_names=zone_names,
        zone_list=zone_list,
        average_over=average_over,
        per_zone=per_zone,
    )
    return_type = 'object'

class mesh(NamedObject[mesh_child], CreatableNamedObjectMixinOld[mesh_child]):
    """
    'mesh' child.
    """
    _version = '222'
    fluent_name = 'mesh'
    _python_name = 'mesh'
    child_object_type = mesh_child
    return_type = 'object'

class custom_vector(String, AllowedValuesMixin):
    """
    'custom_vector' child.
    """
    _version = '222'
    fluent_name = 'custom-vector'
    _python_name = 'custom_vector'
    return_type = 'object'

class field(String, AllowedValuesMixin):
    """
    'field' child.
    """
    _version = '222'
    fluent_name = 'field'
    _python_name = 'field'
    return_type = 'object'

class surfaces(StringList, AllowedValuesMixin):
    """
    'surfaces' child.
    """
    _version = '222'
    fluent_name = 'surfaces'
    _python_name = 'surfaces'
    return_type = 'object'

class geometry_1(StringList, AllowedValuesMixin):
    """
    'geometry' child.
    """
    _version = '222'
    fluent_name = 'geometry'
    _python_name = 'geometry'
    return_type = 'object'

class physics(StringList, AllowedValuesMixin):
    """
    'physics' child.
    """
    _version = '222'
    fluent_name = 'physics'
    _python_name = 'physics'
    return_type = 'object'

class report_type(String, AllowedValuesMixin):
    """
    'report_type' child.
    """
    _version = '222'
    fluent_name = 'report-type'
    _python_name = 'report_type'
    return_type = 'object'

class phase_25(String, AllowedValuesMixin):
    """
    'phase' child.
    """
    _version = '222'
    fluent_name = 'phase'
    _python_name = 'phase'
    return_type = 'object'

class per_surface(Boolean):
    """
    'per_surface' child.
    """
    _version = '222'
    fluent_name = 'per-surface?'
    _python_name = 'per_surface'
    return_type = 'object'

class surface_names(StringList, AllowedValuesMixin):
    """
    'surface_names' child.
    """
    _version = '222'
    fluent_name = 'surface-names'
    _python_name = 'surface_names'
    return_type = 'object'

class surface_ids(StringList, AllowedValuesMixin):
    """
    'surface_ids' child.
    """
    _version = '222'
    fluent_name = 'surface-ids'
    _python_name = 'surface_ids'
    return_type = 'object'

class surface_child(Group):
    """
    'child_object_type' of surface.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'surface_child'
    child_names = ['custom_vector', 'field', 'surfaces', 'geometry', 'physics', 'retain_instantaneous_values', 'report_type', 'phase', 'average_over', 'per_surface', 'old_props', 'surface_names', 'surface_ids']
    _child_classes = dict(
        custom_vector=custom_vector,
        field=field,
        surfaces=surfaces,
        geometry=geometry_1,
        physics=physics,
        retain_instantaneous_values=retain_instantaneous_values,
        report_type=report_type,
        phase=phase_25,
        average_over=average_over,
        per_surface=per_surface,
        old_props=old_props,
        surface_names=surface_names,
        surface_ids=surface_ids,
    )
    return_type = 'object'

class surface(NamedObject[surface_child], CreatableNamedObjectMixinOld[surface_child]):
    """
    'surface' child.
    """
    _version = '222'
    fluent_name = 'surface'
    _python_name = 'surface'
    child_object_type = surface_child
    return_type = 'object'

class expr_list(StringList, AllowedValuesMixin):
    """
    'expr_list' child.
    """
    _version = '222'
    fluent_name = 'expr-list'
    _python_name = 'expr_list'
    return_type = 'object'

class volume_child(Group):
    """
    'child_object_type' of volume.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'volume_child'
    child_names = ['geometry', 'physics', 'field', 'retain_instantaneous_values', 'report_type', 'phase', 'average_over', 'per_zone', 'old_props', 'zone_names', 'expr_list', 'zone_list']
    _child_classes = dict(
        geometry=geometry_1,
        physics=physics,
        field=field,
        retain_instantaneous_values=retain_instantaneous_values,
        report_type=report_type,
        phase=phase_25,
        average_over=average_over,
        per_zone=per_zone,
        old_props=old_props,
        zone_names=zone_names,
        expr_list=expr_list,
        zone_list=zone_list,
    )
    return_type = 'object'

class volume(NamedObject[volume_child], CreatableNamedObjectMixinOld[volume_child]):
    """
    'volume' child.
    """
    _version = '222'
    fluent_name = 'volume'
    _python_name = 'volume'
    child_object_type = volume_child
    return_type = 'object'

class scaled(Boolean):
    """
    'scaled' child.
    """
    _version = '222'
    fluent_name = 'scaled?'
    _python_name = 'scaled'
    return_type = 'object'

class thread_names(StringList, AllowedValuesMixin):
    """
    'thread_names' child.
    """
    _version = '222'
    fluent_name = 'thread-names'
    _python_name = 'thread_names'
    return_type = 'object'

class thread_ids(StringList, AllowedValuesMixin):
    """
    'thread_ids' child.
    """
    _version = '222'
    fluent_name = 'thread-ids'
    _python_name = 'thread_ids'
    return_type = 'object'

class reference_frame(String, AllowedValuesMixin):
    """
    'reference_frame' child.
    """
    _version = '222'
    fluent_name = 'reference-frame'
    _python_name = 'reference_frame'
    return_type = 'object'

class force_vector(RealList):
    """
    'force_vector' child.
    """
    _version = '222'
    fluent_name = 'force-vector'
    _python_name = 'force_vector'
    return_type = 'object'

class force_child(Group):
    """
    'child_object_type' of force.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'force_child'
    child_names = ['retain_instantaneous_values', 'scaled', 'report_type', 'average_over', 'per_zone', 'thread_names', 'thread_ids', 'old_props', 'reference_frame', 'force_vector']
    _child_classes = dict(
        retain_instantaneous_values=retain_instantaneous_values,
        scaled=scaled,
        report_type=report_type,
        average_over=average_over,
        per_zone=per_zone,
        thread_names=thread_names,
        thread_ids=thread_ids,
        old_props=old_props,
        reference_frame=reference_frame,
        force_vector=force_vector,
    )
    return_type = 'object'

class force(NamedObject[force_child], CreatableNamedObjectMixinOld[force_child]):
    """
    'force' child.
    """
    _version = '222'
    fluent_name = 'force'
    _python_name = 'force'
    child_object_type = force_child
    return_type = 'object'

class lift_child(Group):
    """
    'child_object_type' of lift.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'lift_child'
    child_names = ['geometry', 'physics', 'retain_instantaneous_values', 'scaled', 'report_type', 'average_over', 'per_zone', 'thread_names', 'thread_ids', 'old_props', 'reference_frame', 'force_vector']
    _child_classes = dict(
        geometry=geometry_1,
        physics=physics,
        retain_instantaneous_values=retain_instantaneous_values,
        scaled=scaled,
        report_type=report_type,
        average_over=average_over,
        per_zone=per_zone,
        thread_names=thread_names,
        thread_ids=thread_ids,
        old_props=old_props,
        reference_frame=reference_frame,
        force_vector=force_vector,
    )
    return_type = 'object'

class lift(NamedObject[lift_child], CreatableNamedObjectMixinOld[lift_child]):
    """
    'lift' child.
    """
    _version = '222'
    fluent_name = 'lift'
    _python_name = 'lift'
    child_object_type = lift_child
    return_type = 'object'

class drag_child(Group):
    """
    'child_object_type' of drag.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'drag_child'
    child_names = ['geometry', 'physics', 'retain_instantaneous_values', 'scaled', 'report_type', 'average_over', 'per_zone', 'thread_names', 'thread_ids', 'old_props', 'reference_frame', 'force_vector']
    _child_classes = dict(
        geometry=geometry_1,
        physics=physics,
        retain_instantaneous_values=retain_instantaneous_values,
        scaled=scaled,
        report_type=report_type,
        average_over=average_over,
        per_zone=per_zone,
        thread_names=thread_names,
        thread_ids=thread_ids,
        old_props=old_props,
        reference_frame=reference_frame,
        force_vector=force_vector,
    )
    return_type = 'object'

class drag(NamedObject[drag_child], CreatableNamedObjectMixinOld[drag_child]):
    """
    'drag' child.
    """
    _version = '222'
    fluent_name = 'drag'
    _python_name = 'drag'
    child_object_type = drag_child
    return_type = 'object'

class mom_axis(RealList):
    """
    'mom_axis' child.
    """
    _version = '222'
    fluent_name = 'mom-axis'
    _python_name = 'mom_axis'
    return_type = 'object'

class mom_center(RealList):
    """
    'mom_center' child.
    """
    _version = '222'
    fluent_name = 'mom-center'
    _python_name = 'mom_center'
    return_type = 'object'

class moment_child(Group):
    """
    'child_object_type' of moment.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'moment_child'
    child_names = ['retain_instantaneous_values', 'scaled', 'report_type', 'average_over', 'per_zone', 'thread_names', 'thread_ids', 'old_props', 'reference_frame', 'mom_axis', 'mom_center']
    _child_classes = dict(
        retain_instantaneous_values=retain_instantaneous_values,
        scaled=scaled,
        report_type=report_type,
        average_over=average_over,
        per_zone=per_zone,
        thread_names=thread_names,
        thread_ids=thread_ids,
        old_props=old_props,
        reference_frame=reference_frame,
        mom_axis=mom_axis,
        mom_center=mom_center,
    )
    return_type = 'object'

class moment(NamedObject[moment_child], CreatableNamedObjectMixinOld[moment_child]):
    """
    'moment' child.
    """
    _version = '222'
    fluent_name = 'moment'
    _python_name = 'moment'
    child_object_type = moment_child
    return_type = 'object'

class flux_child(Group):
    """
    'child_object_type' of flux.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'flux_child'
    child_names = ['geometry', 'physics', 'retain_instantaneous_values', 'report_type', 'phase', 'average_over', 'per_zone', 'old_props', 'zone_names', 'zone_ids']
    _child_classes = dict(
        geometry=geometry_1,
        physics=physics,
        retain_instantaneous_values=retain_instantaneous_values,
        report_type=report_type,
        phase=phase_25,
        average_over=average_over,
        per_zone=per_zone,
        old_props=old_props,
        zone_names=zone_names,
        zone_ids=zone_ids,
    )
    return_type = 'object'

class flux(NamedObject[flux_child], CreatableNamedObjectMixinOld[flux_child]):
    """
    'flux' child.
    """
    _version = '222'
    fluent_name = 'flux'
    _python_name = 'flux'
    child_object_type = flux_child
    return_type = 'object'

class injection_child(Group):
    """
    'child_object_type' of injection.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'injection_child'
    return_type = 'object'

class injection(NamedObject[injection_child], CreatableNamedObjectMixinOld[injection_child]):
    """
    'injection' child.
    """
    _version = '222'
    fluent_name = 'injection'
    _python_name = 'injection'
    child_object_type = injection_child
    return_type = 'object'

class input_params(StringList, AllowedValuesMixin):
    """
    'input_params' child.
    """
    _version = '222'
    fluent_name = 'input-params'
    _python_name = 'input_params'
    return_type = 'object'

class function_name(String, AllowedValuesMixin):
    """
    'function_name' child.
    """
    _version = '222'
    fluent_name = 'function-name'
    _python_name = 'function_name'
    return_type = 'object'

class user_defined_child(Group):
    """
    'child_object_type' of user_defined.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'user_defined_child'
    child_names = ['retain_instantaneous_values', 'input_params', 'function_name', 'average_over', 'old_props']
    _child_classes = dict(
        retain_instantaneous_values=retain_instantaneous_values,
        input_params=input_params,
        function_name=function_name,
        average_over=average_over,
        old_props=old_props,
    )
    return_type = 'object'

class user_defined(NamedObject[user_defined_child], CreatableNamedObjectMixinOld[user_defined_child]):
    """
    'user_defined' child.
    """
    _version = '222'
    fluent_name = 'user-defined'
    _python_name = 'user_defined'
    child_object_type = user_defined_child
    return_type = 'object'

class normalization(Real):
    """
    'normalization' child.
    """
    _version = '222'
    fluent_name = 'normalization'
    _python_name = 'normalization'
    return_type = 'object'

class integrate_over(Integer):
    """
    'integrate_over' child.
    """
    _version = '222'
    fluent_name = 'integrate-over'
    _python_name = 'integrate_over'
    return_type = 'object'

class aeromechanics_child(Group):
    """
    'child_object_type' of aeromechanics.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'aeromechanics_child'
    child_names = ['normalization', 'integrate_over', 'report_type', 'average_over', 'per_zone', 'old_props', 'thread_names', 'thread_ids']
    _child_classes = dict(
        normalization=normalization,
        integrate_over=integrate_over,
        report_type=report_type,
        average_over=average_over,
        per_zone=per_zone,
        old_props=old_props,
        thread_names=thread_names,
        thread_ids=thread_ids,
    )
    return_type = 'object'

class aeromechanics(NamedObject[aeromechanics_child], CreatableNamedObjectMixinOld[aeromechanics_child]):
    """
    'aeromechanics' child.
    """
    _version = '222'
    fluent_name = 'aeromechanics'
    _python_name = 'aeromechanics'
    child_object_type = aeromechanics_child
    return_type = 'object'

class list_valid_report_names(String, AllowedValuesMixin):
    """
    'list_valid_report_names' child.
    """
    _version = '222'
    fluent_name = 'list-valid-report-names'
    _python_name = 'list_valid_report_names'
    return_type = 'object'

class define(String, AllowedValuesMixin):
    """
    'define' child.
    """
    _version = '222'
    fluent_name = 'define'
    _python_name = 'define'
    return_type = 'object'

class expr_value(Real):
    """
    'expr_value' child.
    """
    _version = '222'
    fluent_name = 'expr-value'
    _python_name = 'expr_value'
    return_type = 'object'

class expression_child(Group):
    """
    'child_object_type' of expression.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'expression_child'
    child_names = ['list_valid_report_names', 'define', 'expr_value', 'average_over', 'old_props']
    _child_classes = dict(
        list_valid_report_names=list_valid_report_names,
        define=define,
        expr_value=expr_value,
        average_over=average_over,
        old_props=old_props,
    )
    return_type = 'object'

class expression(NamedObject[expression_child], CreatableNamedObjectMixinOld[expression_child]):
    """
    'expression' child.
    """
    _version = '222'
    fluent_name = 'expression'
    _python_name = 'expression'
    child_object_type = expression_child
    return_type = 'object'

class custom_child(Group):
    """
    'child_object_type' of custom.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'custom_child'
    return_type = 'object'

class custom(NamedObject[custom_child], CreatableNamedObjectMixinOld[custom_child]):
    """
    'custom' child.
    """
    _version = '222'
    fluent_name = 'custom'
    _python_name = 'custom'
    child_object_type = custom_child
    return_type = 'object'

class report_defs(StringList, AllowedValuesMixin):
    """
    'report_defs' child.
    """
    _version = '222'
    fluent_name = 'report-defs'
    _python_name = 'report_defs'
    return_type = 'object'

class compute_2(Command):
    """
    'compute' command.
    """
    _version = '222'
    fluent_name = 'compute'
    _python_name = 'compute'
    argument_names = ['report_defs']
    _child_classes = dict(
        report_defs=report_defs,
    )
    return_type = 'object'

class report_definitions(Group):
    """
    'report_definitions' child.
    """
    _version = '222'
    fluent_name = 'report-definitions'
    _python_name = 'report_definitions'
    child_names = ['mesh', 'surface', 'volume', 'force', 'lift', 'drag', 'moment', 'flux', 'injection', 'user_defined', 'aeromechanics', 'expression', 'custom']
    command_names = ['compute']
    _child_classes = dict(
        mesh=mesh,
        surface=surface,
        volume=volume,
        force=force,
        lift=lift,
        drag=drag,
        moment=moment,
        flux=flux,
        injection=injection,
        user_defined=user_defined,
        aeromechanics=aeromechanics,
        expression=expression,
        custom=custom,
        compute=compute_2,
    )
    return_type = 'object'

class fmg_initialize(Boolean):
    """
    Initialize using the full-multigrid initialization (FMG).
    """
    _version = '222'
    fluent_name = 'fmg-initialize'
    _python_name = 'fmg_initialize'
    return_type = 'object'

class enabled_1(Boolean):
    """
    Enable/disable localized initialization of turbulent flow variables.
    """
    _version = '222'
    fluent_name = 'enabled?'
    _python_name = 'enabled'
    return_type = 'object'

class turbulent_intensity(Real):
    """
    Turbulent intensity.
    """
    _version = '222'
    fluent_name = 'turbulent-intensity'
    _python_name = 'turbulent_intensity'
    return_type = 'object'

class turbulent_viscosity_ratio(Real):
    """
    Turbulent viscosity ratio.
    """
    _version = '222'
    fluent_name = 'turbulent-viscosity-ratio'
    _python_name = 'turbulent_viscosity_ratio'
    return_type = 'object'

class localized_turb_init(Group):
    """
    'localized_turb_init' child.
    """
    _version = '222'
    fluent_name = 'localized-turb-init'
    _python_name = 'localized_turb_init'
    child_names = ['enabled', 'turbulent_intensity', 'turbulent_viscosity_ratio']
    _child_classes = dict(
        enabled=enabled_1,
        turbulent_intensity=turbulent_intensity,
        turbulent_viscosity_ratio=turbulent_viscosity_ratio,
    )
    return_type = 'object'

class reference_frame_1(String, AllowedValuesMixin):
    """
    Reference frame absolute or relative.
    """
    _version = '222'
    fluent_name = 'reference-frame'
    _python_name = 'reference_frame'
    return_type = 'object'

class viscous_terms(Boolean):
    """
    Enable viscous terms during FMG initialization.
    """
    _version = '222'
    fluent_name = 'viscous-terms?'
    _python_name = 'viscous_terms'
    return_type = 'object'

class species_reactions(Boolean):
    """
    Enable species volumetric reactions during FMG initialization.
    """
    _version = '222'
    fluent_name = 'species-reactions?'
    _python_name = 'species_reactions'
    return_type = 'object'

class set_turbulent_viscosity_ratio(Real):
    """
    Turbulent viscosity ratio used during FMG initialization.
    """
    _version = '222'
    fluent_name = 'set-turbulent-viscosity-ratio'
    _python_name = 'set_turbulent_viscosity_ratio'
    return_type = 'object'

class fmg_options(Group):
    """
    'fmg_options' child.
    """
    _version = '222'
    fluent_name = 'fmg-options'
    _python_name = 'fmg_options'
    child_names = ['viscous_terms', 'species_reactions', 'set_turbulent_viscosity_ratio']
    _child_classes = dict(
        viscous_terms=viscous_terms,
        species_reactions=species_reactions,
        set_turbulent_viscosity_ratio=set_turbulent_viscosity_ratio,
    )
    return_type = 'object'

class number_of_iterations(Integer):
    """
    The number of iterations.
    """
    _version = '222'
    fluent_name = 'number-of-iterations'
    _python_name = 'number_of_iterations'
    return_type = 'object'

class explicit_urf(RealList):
    """
    Explicit URF for scalar equations.
    """
    _version = '222'
    fluent_name = 'explicit-urf'
    _python_name = 'explicit_urf'
    return_type = 'object'

class initial_pressure(Boolean):
    """
    Enable/Disable specified initial pressure on inlets.
    """
    _version = '222'
    fluent_name = 'initial-pressure?'
    _python_name = 'initial_pressure'
    return_type = 'object'

class external_aero(Boolean):
    """
    Enable/Disable external-aero favorable settings.
    """
    _version = '222'
    fluent_name = 'external-aero?'
    _python_name = 'external_aero'
    return_type = 'object'

class const_velocity(Boolean):
    """
    Enable/Disable constant velocity magnitude.
    """
    _version = '222'
    fluent_name = 'const-velocity?'
    _python_name = 'const_velocity'
    return_type = 'object'

class general_settings(Group):
    """
    The general settings object.
    """
    _version = '222'
    fluent_name = 'general-settings'
    _python_name = 'general_settings'
    child_names = ['number_of_iterations', 'explicit_urf', 'reference_frame', 'initial_pressure', 'external_aero', 'const_velocity']
    _child_classes = dict(
        number_of_iterations=number_of_iterations,
        explicit_urf=explicit_urf,
        reference_frame=reference_frame_1,
        initial_pressure=initial_pressure,
        external_aero=external_aero,
        const_velocity=const_velocity,
    )
    return_type = 'object'

class averaged_turbulent_parameters(Boolean):
    """
    Enable/Disable averaged turbulent parameters.
    """
    _version = '222'
    fluent_name = 'averaged-turbulent-parameters?'
    _python_name = 'averaged_turbulent_parameters'
    return_type = 'object'

class viscosity_ratio_1(Real):
    """
    Viscosity ratio.
    """
    _version = '222'
    fluent_name = 'viscosity-ratio'
    _python_name = 'viscosity_ratio'
    return_type = 'object'

class turbulent_setting(Group):
    """
    The turbulent settings object.
    """
    _version = '222'
    fluent_name = 'turbulent-setting'
    _python_name = 'turbulent_setting'
    child_names = ['averaged_turbulent_parameters', 'turbulent_intensity', 'viscosity_ratio']
    _child_classes = dict(
        averaged_turbulent_parameters=averaged_turbulent_parameters,
        turbulent_intensity=turbulent_intensity,
        viscosity_ratio=viscosity_ratio_1,
    )
    return_type = 'object'

class set_hybrid_init_options(Group):
    """
    'set_hybrid_init_options' child.
    """
    _version = '222'
    fluent_name = 'set-hybrid-init-options'
    _python_name = 'set_hybrid_init_options'
    child_names = ['general_settings', 'turbulent_setting']
    _child_classes = dict(
        general_settings=general_settings,
        turbulent_setting=turbulent_setting,
    )
    return_type = 'object'

class patch_reconstructed_interface(Boolean):
    """
    Enable/Disable patch reconstructed interface.
    """
    _version = '222'
    fluent_name = 'patch-reconstructed-interface?'
    _python_name = 'patch_reconstructed_interface'
    return_type = 'object'

class use_volumetric_smoothing(Boolean):
    """
    Enable/Disable volumetric smoothing.
    """
    _version = '222'
    fluent_name = 'use-volumetric-smoothing?'
    _python_name = 'use_volumetric_smoothing'
    return_type = 'object'

class smoothing_relaxation_factor(Real):
    """
    Smoothing relaxation factor (min : 0, max : 1).
    """
    _version = '222'
    fluent_name = 'smoothing-relaxation-factor'
    _python_name = 'smoothing_relaxation_factor'
    return_type = 'object'

class execute_smoothing(Command):
    """
    Execute volumetric smoothing for volume fraction.
    """
    _version = '222'
    fluent_name = 'execute-smoothing'
    _python_name = 'execute_smoothing'
    return_type = 'object'

class vof_smooth_options(Group):
    """
    'vof_smooth_options' child.
    """
    _version = '222'
    fluent_name = 'vof-smooth-options'
    _python_name = 'vof_smooth_options'
    child_names = ['patch_reconstructed_interface', 'use_volumetric_smoothing', 'smoothing_relaxation_factor']
    command_names = ['execute_smoothing']
    _child_classes = dict(
        patch_reconstructed_interface=patch_reconstructed_interface,
        use_volumetric_smoothing=use_volumetric_smoothing,
        smoothing_relaxation_factor=smoothing_relaxation_factor,
        execute_smoothing=execute_smoothing,
    )
    return_type = 'object'

class patch(Group):
    """
    'patch' child.
    """
    _version = '222'
    fluent_name = 'patch'
    _python_name = 'patch'
    child_names = ['vof_smooth_options']
    _child_classes = dict(
        vof_smooth_options=vof_smooth_options,
    )
    return_type = 'object'

class standard_initialize(Command):
    """
    Initialize the flow field with the current default values.
    """
    _version = '222'
    fluent_name = 'standard-initialize'
    _python_name = 'standard_initialize'
    return_type = 'object'

class hybrid_initialize(Command):
    """
    Initialize using the hybrid initialization method.
    """
    _version = '222'
    fluent_name = 'hybrid-initialize'
    _python_name = 'hybrid_initialize'
    return_type = 'object'

class dpm_reset(Command):
    """
    Reset discrete phase source terms to zero.
    """
    _version = '222'
    fluent_name = 'dpm-reset'
    _python_name = 'dpm_reset'
    return_type = 'object'

class lwf_reset(Command):
    """
    Delete wall film particles and initialize wall film variables to zero.
    """
    _version = '222'
    fluent_name = 'lwf-reset'
    _python_name = 'lwf_reset'
    return_type = 'object'

class init_flow_statistics(Command):
    """
    Initialize statistics.
    """
    _version = '222'
    fluent_name = 'init-flow-statistics'
    _python_name = 'init_flow_statistics'
    return_type = 'object'

class set_ramping_length(Boolean):
    """
    Enable/Disable ramping length and initialize acoustics.
    """
    _version = '222'
    fluent_name = 'set-ramping-length?'
    _python_name = 'set_ramping_length'
    return_type = 'object'

class number_of_timesteps(Integer):
    """
    Number of timesteps for ramping of sources.
    """
    _version = '222'
    fluent_name = 'number-of-timesteps'
    _python_name = 'number_of_timesteps'
    return_type = 'object'

class init_acoustics_options(Command):
    """
    'init_acoustics_options' command.
    """
    _version = '222'
    fluent_name = 'init-acoustics-options'
    _python_name = 'init_acoustics_options'
    argument_names = ['set_ramping_length', 'number_of_timesteps']
    _child_classes = dict(
        set_ramping_length=set_ramping_length,
        number_of_timesteps=number_of_timesteps,
    )
    return_type = 'object'

class initialization(Group):
    """
    'initialization' child.
    """
    _version = '222'
    fluent_name = 'initialization'
    _python_name = 'initialization'
    child_names = ['fmg_initialize', 'localized_turb_init', 'reference_frame', 'fmg_options', 'set_hybrid_init_options', 'patch']
    command_names = ['standard_initialize', 'hybrid_initialize', 'dpm_reset', 'lwf_reset', 'init_flow_statistics', 'init_acoustics_options']
    _child_classes = dict(
        fmg_initialize=fmg_initialize,
        localized_turb_init=localized_turb_init,
        reference_frame=reference_frame_1,
        fmg_options=fmg_options,
        set_hybrid_init_options=set_hybrid_init_options,
        patch=patch,
        standard_initialize=standard_initialize,
        hybrid_initialize=hybrid_initialize,
        dpm_reset=dpm_reset,
        lwf_reset=lwf_reset,
        init_flow_statistics=init_flow_statistics,
        init_acoustics_options=init_acoustics_options,
    )
    return_type = 'object'

class enabled_2(Boolean):
    """
    'enabled' child.
    """
    _version = '222'
    fluent_name = 'enabled?'
    _python_name = 'enabled'
    return_type = 'object'

class user_defined_timestep(String, AllowedValuesMixin):
    """
    'user_defined_timestep' child.
    """
    _version = '222'
    fluent_name = 'user-defined-timestep'
    _python_name = 'user_defined_timestep'
    return_type = 'object'

class error_tolerance(Real):
    """
    Truncation Error Tolerance.
    """
    _version = '222'
    fluent_name = 'error-tolerance'
    _python_name = 'error_tolerance'
    return_type = 'object'

class time_end(Real):
    """
    Total Simulation Time.
    """
    _version = '222'
    fluent_name = 'time-end'
    _python_name = 'time_end'
    return_type = 'object'

class min_time_step(Real):
    """
    Minimum Time Step Size.
    """
    _version = '222'
    fluent_name = 'min-time-step'
    _python_name = 'min_time_step'
    return_type = 'object'

class max_time_step(Real):
    """
    Maximum Time Step Size.
    """
    _version = '222'
    fluent_name = 'max-time-step'
    _python_name = 'max_time_step'
    return_type = 'object'

class min_step_change_factor(Real):
    """
    Minimum Step Change Factor.
    """
    _version = '222'
    fluent_name = 'min-step-change-factor'
    _python_name = 'min_step_change_factor'
    return_type = 'object'

class max_step_change_factor(Real):
    """
    Maximum Step Change Factor.
    """
    _version = '222'
    fluent_name = 'max-step-change-factor'
    _python_name = 'max_step_change_factor'
    return_type = 'object'

class fixed_time_steps(Integer):
    """
    Number of Fixed Time Steps.
    """
    _version = '222'
    fluent_name = 'fixed-time-steps'
    _python_name = 'fixed_time_steps'
    return_type = 'object'

class adaptive_time_stepping(Group):
    """
    'adaptive_time_stepping' child.
    """
    _version = '222'
    fluent_name = 'adaptive-time-stepping'
    _python_name = 'adaptive_time_stepping'
    child_names = ['enabled', 'user_defined_timestep', 'error_tolerance', 'time_end', 'min_time_step', 'max_time_step', 'min_step_change_factor', 'max_step_change_factor', 'fixed_time_steps']
    _child_classes = dict(
        enabled=enabled_2,
        user_defined_timestep=user_defined_timestep,
        error_tolerance=error_tolerance,
        time_end=time_end,
        min_time_step=min_time_step,
        max_time_step=max_time_step,
        min_step_change_factor=min_step_change_factor,
        max_step_change_factor=max_step_change_factor,
        fixed_time_steps=fixed_time_steps,
    )
    return_type = 'object'

class enalbled(Boolean):
    """
    'enalbled' child.
    """
    _version = '222'
    fluent_name = 'enalbled?'
    _python_name = 'enalbled'
    return_type = 'object'

class desired_cfl(Real):
    """
    Courant Number.
    """
    _version = '222'
    fluent_name = 'desired-cfl'
    _python_name = 'desired_cfl'
    return_type = 'object'

class initial_time_step(Real):
    """
    Initial Time Step Size.
    """
    _version = '222'
    fluent_name = 'initial-time-step'
    _python_name = 'initial_time_step'
    return_type = 'object'

class max_fixed_time_step(Integer):
    """
    Number of Fixed Time Steps.
    """
    _version = '222'
    fluent_name = 'max-fixed-time-step'
    _python_name = 'max_fixed_time_step'
    return_type = 'object'

class update_interval_time_step_size(Integer):
    """
    Time Step Size Update Interval.
    """
    _version = '222'
    fluent_name = 'update-interval-time-step-size'
    _python_name = 'update_interval_time_step_size'
    return_type = 'object'

class cfl_based_adaptive_time_stepping(Group):
    """
    'cfl_based_adaptive_time_stepping' child.
    """
    _version = '222'
    fluent_name = 'cfl-based-adaptive-time-stepping'
    _python_name = 'cfl_based_adaptive_time_stepping'
    child_names = ['enalbled', 'user_defined_timestep', 'desired_cfl', 'time_end', 'initial_time_step', 'max_fixed_time_step', 'update_interval_time_step_size', 'min_time_step', 'max_time_step', 'min_step_change_factor', 'max_step_change_factor']
    _child_classes = dict(
        enalbled=enalbled,
        user_defined_timestep=user_defined_timestep,
        desired_cfl=desired_cfl,
        time_end=time_end,
        initial_time_step=initial_time_step,
        max_fixed_time_step=max_fixed_time_step,
        update_interval_time_step_size=update_interval_time_step_size,
        min_time_step=min_time_step,
        max_time_step=max_time_step,
        min_step_change_factor=min_step_change_factor,
        max_step_change_factor=max_step_change_factor,
    )
    return_type = 'object'

class data_sampling_1(Boolean):
    """
    'data_sampling' child.
    """
    _version = '222'
    fluent_name = 'data-sampling?'
    _python_name = 'data_sampling'
    return_type = 'object'

class sampling_interval(Integer):
    """
    Sampling interval.
    """
    _version = '222'
    fluent_name = 'sampling-interval'
    _python_name = 'sampling_interval'
    return_type = 'object'

class statistics_shear_stress(Boolean):
    """
    Enable/Disable statistics for flow shear stresses.
    """
    _version = '222'
    fluent_name = 'statistics-shear-stress?'
    _python_name = 'statistics_shear_stress'
    return_type = 'object'

class statistics_heat_flux(Boolean):
    """
    Enable/Disable statistics for flow heat fluxes.
    """
    _version = '222'
    fluent_name = 'statistics-heat-flux?'
    _python_name = 'statistics_heat_flux'
    return_type = 'object'

class wall_statistics(Boolean):
    """
    Enable/Disable wall statistics.
    """
    _version = '222'
    fluent_name = 'wall-statistics?'
    _python_name = 'wall_statistics'
    return_type = 'object'

class force_statistics(Boolean):
    """
    Enable/Disable force statistics.
    """
    _version = '222'
    fluent_name = 'force-statistics?'
    _python_name = 'force_statistics'
    return_type = 'object'

class time_statistics_dpm(Boolean):
    """
    Enable/Disable statistics for DPM variables.
    """
    _version = '222'
    fluent_name = 'time-statistics-dpm?'
    _python_name = 'time_statistics_dpm'
    return_type = 'object'

class species_list(StringList, AllowedValuesMixin):
    """
    Enable/Disable statistics for sps.
    """
    _version = '222'
    fluent_name = 'species-list'
    _python_name = 'species_list'
    return_type = 'object'

class statistics_mixture_fraction(Boolean):
    """
    Enable/Disable statistics for mixture fraction.
    """
    _version = '222'
    fluent_name = 'statistics-mixture-fraction?'
    _python_name = 'statistics_mixture_fraction'
    return_type = 'object'

class statistics_reaction_progress(Boolean):
    """
    Enable/Disable statistics for reaction progress.
    """
    _version = '222'
    fluent_name = 'statistics-reaction-progress?'
    _python_name = 'statistics_reaction_progress'
    return_type = 'object'

class save_cff_unsteady_statistics(Boolean):
    """
    Enable/Disable statistics for Custom Field Functions.
    """
    _version = '222'
    fluent_name = 'save-cff-unsteady-statistics?'
    _python_name = 'save_cff_unsteady_statistics'
    return_type = 'object'

class udf_cf_names(StringList, AllowedValuesMixin):
    """
    'udf_cf_names' child.
    """
    _version = '222'
    fluent_name = 'udf-cf-names'
    _python_name = 'udf_cf_names'
    return_type = 'object'

class setup_unsteady_statistics(Command):
    """
    'setup_unsteady_statistics' command.
    """
    _version = '222'
    fluent_name = 'setup-unsteady-statistics'
    _python_name = 'setup_unsteady_statistics'
    argument_names = ['udf_cf_names']
    _child_classes = dict(
        udf_cf_names=udf_cf_names,
    )
    return_type = 'object'

class data_sampling(Group):
    """
    'data_sampling' child.
    """
    _version = '222'
    fluent_name = 'data-sampling'
    _python_name = 'data_sampling'
    child_names = ['data_sampling', 'sampling_interval', 'statistics_shear_stress', 'statistics_heat_flux', 'wall_statistics', 'force_statistics', 'time_statistics_dpm', 'species_list', 'statistics_mixture_fraction', 'statistics_reaction_progress', 'save_cff_unsteady_statistics']
    command_names = ['setup_unsteady_statistics']
    _child_classes = dict(
        data_sampling=data_sampling_1,
        sampling_interval=sampling_interval,
        statistics_shear_stress=statistics_shear_stress,
        statistics_heat_flux=statistics_heat_flux,
        wall_statistics=wall_statistics,
        force_statistics=force_statistics,
        time_statistics_dpm=time_statistics_dpm,
        species_list=species_list,
        statistics_mixture_fraction=statistics_mixture_fraction,
        statistics_reaction_progress=statistics_reaction_progress,
        save_cff_unsteady_statistics=save_cff_unsteady_statistics,
        setup_unsteady_statistics=setup_unsteady_statistics,
    )
    return_type = 'object'

class specified_time_step(Boolean):
    """
    Use specified time step or courant number.
    """
    _version = '222'
    fluent_name = 'specified-time-step'
    _python_name = 'specified_time_step'
    return_type = 'object'

class incremental_time(Real):
    """
    Incremental Time.
    """
    _version = '222'
    fluent_name = 'incremental-time'
    _python_name = 'incremental_time'
    return_type = 'object'

class max_iterations_per_time_step(Integer):
    """
    Max Iterations/Time Step.
    """
    _version = '222'
    fluent_name = 'max-iterations-per-time-step'
    _python_name = 'max_iterations_per_time_step'
    return_type = 'object'

class number_of_time_steps(Integer):
    """
    Inceremtal number of Time steps.
    """
    _version = '222'
    fluent_name = 'number-of-time-steps'
    _python_name = 'number_of_time_steps'
    return_type = 'object'

class total_number_of_time_steps(Integer):
    """
    Total number of Time steps.
    """
    _version = '222'
    fluent_name = 'total-number-of-time-steps'
    _python_name = 'total_number_of_time_steps'
    return_type = 'object'

class total_time(Real):
    """
    Total Simulation Time.
    """
    _version = '222'
    fluent_name = 'total-time'
    _python_name = 'total_time'
    return_type = 'object'

class time_step_size(Real):
    """
    The physical time step size.
    """
    _version = '222'
    fluent_name = 'time-step-size'
    _python_name = 'time_step_size'
    return_type = 'object'

class solution_status(Boolean):
    """
    Activate the simulation status panel.
    """
    _version = '222'
    fluent_name = 'solution-status'
    _python_name = 'solution_status'
    return_type = 'object'

class extrapolate_vars(Boolean):
    """
    The extrapolation object.
    """
    _version = '222'
    fluent_name = 'extrapolate-vars'
    _python_name = 'extrapolate_vars'
    return_type = 'object'

class max_flow_time(Real):
    """
    Maximum flow time.
    """
    _version = '222'
    fluent_name = 'max-flow-time'
    _python_name = 'max_flow_time'
    return_type = 'object'

class control_time_step_size_variation(Boolean):
    """
    Control time step size variation.
    """
    _version = '222'
    fluent_name = 'control-time-step-size-variation?'
    _python_name = 'control_time_step_size_variation'
    return_type = 'object'

class use_average_cfl(Boolean):
    """
    Use Averaged CFL condition rather than maximum CFL condition.
    """
    _version = '222'
    fluent_name = 'use-average-cfl?'
    _python_name = 'use_average_cfl'
    return_type = 'object'

class cfl_type(Integer):
    """
    CFL type .
    """
    _version = '222'
    fluent_name = 'cfl-type'
    _python_name = 'cfl_type'
    return_type = 'object'

class courant_number_1(Real):
    """
    Courant Number.
    """
    _version = '222'
    fluent_name = 'courant-number'
    _python_name = 'courant_number'
    return_type = 'object'

class initial_time_step_size(Real):
    """
    Initial Time Step Size.
    """
    _version = '222'
    fluent_name = 'initial-time-step-size'
    _python_name = 'initial_time_step_size'
    return_type = 'object'

class fixed_time_step_size(Integer):
    """
    Number of Fixed Time Steps.
    """
    _version = '222'
    fluent_name = 'fixed-time-step-size'
    _python_name = 'fixed_time_step_size'
    return_type = 'object'

class min_time_step_size(Real):
    """
    Minimum Time Step Size.
    """
    _version = '222'
    fluent_name = 'min-time-step-size'
    _python_name = 'min_time_step_size'
    return_type = 'object'

class max_time_step_size(Real):
    """
    Maximum Time Step Size.
    """
    _version = '222'
    fluent_name = 'max-time-step-size'
    _python_name = 'max_time_step_size'
    return_type = 'object'

class update_interval(Integer):
    """
    Time Step Size Update Interval.
    """
    _version = '222'
    fluent_name = 'update-interval'
    _python_name = 'update_interval'
    return_type = 'object'

class cfl_based_time_stepping(Group):
    """
    'cfl_based_time_stepping' child.
    """
    _version = '222'
    fluent_name = 'cfl-based-time-stepping'
    _python_name = 'cfl_based_time_stepping'
    child_names = ['courant_number', 'initial_time_step_size', 'fixed_time_step_size', 'min_time_step_size', 'max_time_step_size', 'min_step_change_factor', 'max_step_change_factor', 'update_interval']
    _child_classes = dict(
        courant_number=courant_number_1,
        initial_time_step_size=initial_time_step_size,
        fixed_time_step_size=fixed_time_step_size,
        min_time_step_size=min_time_step_size,
        max_time_step_size=max_time_step_size,
        min_step_change_factor=min_step_change_factor,
        max_step_change_factor=max_step_change_factor,
        update_interval=update_interval,
    )
    return_type = 'object'

class error_tolerance_1(Real):
    """
    Error Tolerance.
    """
    _version = '222'
    fluent_name = 'error-tolerance'
    _python_name = 'error_tolerance'
    return_type = 'object'

class error_based_time_stepping(Group):
    """
    'error_based_time_stepping' child.
    """
    _version = '222'
    fluent_name = 'error-based-time-stepping'
    _python_name = 'error_based_time_stepping'
    child_names = ['error_tolerance', 'initial_time_step_size', 'fixed_time_step_size', 'min_time_step_size', 'max_time_step_size', 'min_step_change_factor', 'max_step_change_factor', 'update_interval']
    _child_classes = dict(
        error_tolerance=error_tolerance_1,
        initial_time_step_size=initial_time_step_size,
        fixed_time_step_size=fixed_time_step_size,
        min_time_step_size=min_time_step_size,
        max_time_step_size=max_time_step_size,
        min_step_change_factor=min_step_change_factor,
        max_step_change_factor=max_step_change_factor,
        update_interval=update_interval,
    )
    return_type = 'object'

class undo_timestep(Boolean):
    """
    Undo the previous time step.
    """
    _version = '222'
    fluent_name = 'undo-timestep?'
    _python_name = 'undo_timestep'
    return_type = 'object'

class predict_next(Boolean):
    """
    Applies a predictor algorithm for computing initial condition at time step n+1.
    """
    _version = '222'
    fluent_name = 'predict-next?'
    _python_name = 'predict_next'
    return_type = 'object'

class rotating_mesh_flow_predictor(Boolean):
    """
    Improve prediction of flow field at time step n+1 for rotating mesh.
    """
    _version = '222'
    fluent_name = 'rotating-mesh-flow-predictor?'
    _python_name = 'rotating_mesh_flow_predictor'
    return_type = 'object'

class global_courant_number(Real):
    """
    Global Courant Number.
    """
    _version = '222'
    fluent_name = 'global-courant-number'
    _python_name = 'global_courant_number'
    return_type = 'object'

class mp_specific_time_stepping(Group):
    """
    'mp_specific_time_stepping' child.
    """
    _version = '222'
    fluent_name = 'mp-specific-time-stepping'
    _python_name = 'mp_specific_time_stepping'
    child_names = ['enabled', 'global_courant_number', 'initial_time_step_size', 'fixed_time_step_size', 'min_time_step_size', 'max_time_step_size', 'min_step_change_factor', 'max_step_change_factor', 'update_interval']
    _child_classes = dict(
        enabled=enabled_2,
        global_courant_number=global_courant_number,
        initial_time_step_size=initial_time_step_size,
        fixed_time_step_size=fixed_time_step_size,
        min_time_step_size=min_time_step_size,
        max_time_step_size=max_time_step_size,
        min_step_change_factor=min_step_change_factor,
        max_step_change_factor=max_step_change_factor,
        update_interval=update_interval,
    )
    return_type = 'object'

class udf_hook(String, AllowedValuesMixin):
    """
    'udf_hook' child.
    """
    _version = '222'
    fluent_name = 'udf-hook'
    _python_name = 'udf_hook'
    return_type = 'object'

class transient_controls(Group):
    """
    'transient_controls' child.
    """
    _version = '222'
    fluent_name = 'transient-controls'
    _python_name = 'transient_controls'
    child_names = ['type', 'method', 'specified_time_step', 'incremental_time', 'max_iterations_per_time_step', 'number_of_time_steps', 'total_number_of_time_steps', 'total_time', 'time_step_size', 'solution_status', 'extrapolate_vars', 'max_flow_time', 'control_time_step_size_variation', 'use_average_cfl', 'cfl_type', 'cfl_based_time_stepping', 'error_based_time_stepping', 'undo_timestep', 'predict_next', 'rotating_mesh_flow_predictor', 'mp_specific_time_stepping', 'udf_hook']
    _child_classes = dict(
        type=type_1,
        method=method,
        specified_time_step=specified_time_step,
        incremental_time=incremental_time,
        max_iterations_per_time_step=max_iterations_per_time_step,
        number_of_time_steps=number_of_time_steps,
        total_number_of_time_steps=total_number_of_time_steps,
        total_time=total_time,
        time_step_size=time_step_size,
        solution_status=solution_status,
        extrapolate_vars=extrapolate_vars,
        max_flow_time=max_flow_time,
        control_time_step_size_variation=control_time_step_size_variation,
        use_average_cfl=use_average_cfl,
        cfl_type=cfl_type,
        cfl_based_time_stepping=cfl_based_time_stepping,
        error_based_time_stepping=error_based_time_stepping,
        undo_timestep=undo_timestep,
        predict_next=predict_next,
        rotating_mesh_flow_predictor=rotating_mesh_flow_predictor,
        mp_specific_time_stepping=mp_specific_time_stepping,
        udf_hook=udf_hook,
    )
    return_type = 'object'

class number_of_total_periods(Integer):
    """
    Number of total periods.
    """
    _version = '222'
    fluent_name = 'number-of-total-periods'
    _python_name = 'number_of_total_periods'
    return_type = 'object'

class max_iteration_per_step(Integer):
    """
    Maximum Number of iterations per time step.
    """
    _version = '222'
    fluent_name = 'max-iteration-per-step'
    _python_name = 'max_iteration_per_step'
    return_type = 'object'

class postprocess(Boolean):
    """
    Enable/Disable Postprocess pollutant solution?.
    """
    _version = '222'
    fluent_name = 'postprocess?'
    _python_name = 'postprocess'
    return_type = 'object'

class num_of_post_iter_per_timestep(Integer):
    """
    Number of post-processing iterations per time step.
    """
    _version = '222'
    fluent_name = 'num-of-post-iter-per-timestep'
    _python_name = 'num_of_post_iter_per_timestep'
    return_type = 'object'

class dual_time_iterate(Command):
    """
    Perform unsteady iterations.
    
    Parameters
    ----------
        number_of_total_periods : int
            Number of total periods.
        number_of_time_steps : int
            Inceremtal number of Time steps.
        total_number_of_time_steps : int
            Total number of Time steps.
        total_time : real
            Total Simulation Time.
        incremental_time : real
            Incremental Time.
        max_iteration_per_step : int
            Maximum Number of iterations per time step.
        postprocess : bool
            Enable/Disable Postprocess pollutant solution?.
        num_of_post_iter_per_timestep : int
            Number of post-processing iterations per time step.
    """
    _version = '222'
    fluent_name = 'dual-time-iterate'
    _python_name = 'dual_time_iterate'
    argument_names = ['number_of_total_periods', 'number_of_time_steps', 'total_number_of_time_steps', 'total_time', 'incremental_time', 'max_iteration_per_step', 'postprocess', 'num_of_post_iter_per_timestep']
    _child_classes = dict(
        number_of_total_periods=number_of_total_periods,
        number_of_time_steps=number_of_time_steps,
        total_number_of_time_steps=total_number_of_time_steps,
        total_time=total_time,
        incremental_time=incremental_time,
        max_iteration_per_step=max_iteration_per_step,
        postprocess=postprocess,
        num_of_post_iter_per_timestep=num_of_post_iter_per_timestep,
    )
    return_type = 'object'

class number_of_iterations_1(Integer):
    """
    Inceremtal number of Time steps.
    """
    _version = '222'
    fluent_name = 'number-of-iterations'
    _python_name = 'number_of_iterations'
    return_type = 'object'

class iterate(Command):
    """
    Perform a specified number of iterations.
    
    Parameters
    ----------
        number_of_iterations : int
            Inceremtal number of Time steps.
    """
    _version = '222'
    fluent_name = 'iterate'
    _python_name = 'iterate'
    argument_names = ['number_of_iterations']
    _child_classes = dict(
        number_of_iterations=number_of_iterations_1,
    )
    return_type = 'object'

class run_calculation(Group):
    """
    'run_calculation' child.
    """
    _version = '222'
    fluent_name = 'run-calculation'
    _python_name = 'run_calculation'
    child_names = ['adaptive_time_stepping', 'cfl_based_adaptive_time_stepping', 'data_sampling', 'transient_controls']
    command_names = ['dual_time_iterate', 'iterate']
    _child_classes = dict(
        adaptive_time_stepping=adaptive_time_stepping,
        cfl_based_adaptive_time_stepping=cfl_based_adaptive_time_stepping,
        data_sampling=data_sampling,
        transient_controls=transient_controls,
        dual_time_iterate=dual_time_iterate,
        iterate=iterate,
    )
    return_type = 'object'

class solution(Group):
    """
    'solution' child.
    """
    _version = '222'
    fluent_name = 'solution'
    _python_name = 'solution'
    child_names = ['controls', 'methods', 'report_definitions', 'initialization', 'run_calculation']
    _child_classes = dict(
        controls=controls,
        methods=methods,
        report_definitions=report_definitions,
        initialization=initialization,
        run_calculation=run_calculation,
    )
    return_type = 'object'

class object_name(String, AllowedValuesMixin):
    """
    'object_name' child.
    """
    _version = '222'
    fluent_name = 'object-name'
    _python_name = 'object_name'
    return_type = 'object'

class display(Command):
    """
    'display' command.
    """
    _version = '222'
    fluent_name = 'display'
    _python_name = 'display'
    argument_names = ['object_name']
    _child_classes = dict(
        object_name=object_name,
    )
    return_type = 'object'

class nodes(Boolean):
    """
    'nodes' child.
    """
    _version = '222'
    fluent_name = 'nodes?'
    _python_name = 'nodes'
    return_type = 'object'

class edges(Boolean):
    """
    'edges' child.
    """
    _version = '222'
    fluent_name = 'edges?'
    _python_name = 'edges'
    return_type = 'object'

class faces(Boolean):
    """
    'faces' child.
    """
    _version = '222'
    fluent_name = 'faces?'
    _python_name = 'faces'
    return_type = 'object'

class partitions(Boolean):
    """
    'partitions' child.
    """
    _version = '222'
    fluent_name = 'partitions?'
    _python_name = 'partitions'
    return_type = 'object'

class overset_2(Boolean):
    """
    'overset' child.
    """
    _version = '222'
    fluent_name = 'overset?'
    _python_name = 'overset'
    return_type = 'object'

class gap(Boolean):
    """
    'gap' child.
    """
    _version = '222'
    fluent_name = 'gap?'
    _python_name = 'gap'
    return_type = 'object'

class options_4(Group):
    """
    'options' child.
    """
    _version = '222'
    fluent_name = 'options'
    _python_name = 'options'
    child_names = ['nodes', 'edges', 'faces', 'partitions', 'overset', 'gap']
    _child_classes = dict(
        nodes=nodes,
        edges=edges,
        faces=faces,
        partitions=partitions,
        overset=overset_2,
        gap=gap,
    )
    return_type = 'object'

class all(Boolean):
    """
    'all' child.
    """
    _version = '222'
    fluent_name = 'all'
    _python_name = 'all'
    return_type = 'object'

class feature_angle(Real):
    """
    'feature_angle' child.
    """
    _version = '222'
    fluent_name = 'feature-angle'
    _python_name = 'feature_angle'
    return_type = 'object'

class feature(Group):
    """
    'feature' child.
    """
    _version = '222'
    fluent_name = 'feature'
    _python_name = 'feature'
    child_names = ['feature_angle']
    _child_classes = dict(
        feature_angle=feature_angle,
    )
    return_type = 'object'

class outline(Boolean):
    """
    'outline' child.
    """
    _version = '222'
    fluent_name = 'outline'
    _python_name = 'outline'
    return_type = 'object'

class edge_type(Group):
    """
    'edge_type' child.
    """
    _version = '222'
    fluent_name = 'edge-type'
    _python_name = 'edge_type'
    child_names = ['option', 'all', 'feature', 'outline']
    _child_classes = dict(
        option=option,
        all=all,
        feature=feature,
        outline=outline,
    )
    return_type = 'object'

class shrink_factor(Real):
    """
    'shrink_factor' child.
    """
    _version = '222'
    fluent_name = 'shrink-factor'
    _python_name = 'shrink_factor'
    return_type = 'object'

class surfaces_list(StringList, AllowedValuesMixin):
    """
    'surfaces_list' child.
    """
    _version = '222'
    fluent_name = 'surfaces-list'
    _python_name = 'surfaces_list'
    return_type = 'object'

class type_2(Group):
    """
    'type' child.
    """
    _version = '222'
    fluent_name = 'type'
    _python_name = 'type'
    return_type = 'object'

class id(Boolean):
    """
    'id' child.
    """
    _version = '222'
    fluent_name = 'id'
    _python_name = 'id'
    return_type = 'object'

class normal(Boolean):
    """
    'normal' child.
    """
    _version = '222'
    fluent_name = 'normal'
    _python_name = 'normal'
    return_type = 'object'

class partition(Boolean):
    """
    'partition' child.
    """
    _version = '222'
    fluent_name = 'partition'
    _python_name = 'partition'
    return_type = 'object'

class automatic(Group):
    """
    'automatic' child.
    """
    _version = '222'
    fluent_name = 'automatic'
    _python_name = 'automatic'
    child_names = ['option', 'type', 'id', 'normal', 'partition']
    _child_classes = dict(
        option=option,
        type=type_2,
        id=id,
        normal=normal,
        partition=partition,
    )
    return_type = 'object'

class faces_1(String, AllowedValuesMixin):
    """
    'faces' child.
    """
    _version = '222'
    fluent_name = 'faces'
    _python_name = 'faces'
    return_type = 'object'

class edges_1(String, AllowedValuesMixin):
    """
    'edges' child.
    """
    _version = '222'
    fluent_name = 'edges'
    _python_name = 'edges'
    return_type = 'object'

class nodes_1(String, AllowedValuesMixin):
    """
    'nodes' child.
    """
    _version = '222'
    fluent_name = 'nodes'
    _python_name = 'nodes'
    return_type = 'object'

class material_color(String, AllowedValuesMixin):
    """
    'material_color' child.
    """
    _version = '222'
    fluent_name = 'material-color'
    _python_name = 'material_color'
    return_type = 'object'

class manual(Group):
    """
    'manual' child.
    """
    _version = '222'
    fluent_name = 'manual'
    _python_name = 'manual'
    child_names = ['faces', 'edges', 'nodes', 'material_color']
    _child_classes = dict(
        faces=faces_1,
        edges=edges_1,
        nodes=nodes_1,
        material_color=material_color,
    )
    return_type = 'object'

class coloring(Group):
    """
    'coloring' child.
    """
    _version = '222'
    fluent_name = 'coloring'
    _python_name = 'coloring'
    child_names = ['option', 'automatic', 'manual']
    _child_classes = dict(
        option=option,
        automatic=automatic,
        manual=manual,
    )
    return_type = 'object'

class display_state_name(String, AllowedValuesMixin):
    """
    'display_state_name' child.
    """
    _version = '222'
    fluent_name = 'display-state-name'
    _python_name = 'display_state_name'
    return_type = 'object'

class display_1(Command):
    """
    'display' command.
    """
    _version = '222'
    fluent_name = 'display'
    _python_name = 'display'
    return_type = 'object'

class mesh_1_child(Group):
    """
    'child_object_type' of mesh.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'mesh_child'
    child_names = ['name', 'options', 'edge_type', 'shrink_factor', 'surfaces_list', 'coloring', 'display_state_name', 'physics', 'geometry', 'surfaces']
    command_names = ['display']
    _child_classes = dict(
        name=name,
        options=options_4,
        edge_type=edge_type,
        shrink_factor=shrink_factor,
        surfaces_list=surfaces_list,
        coloring=coloring,
        display_state_name=display_state_name,
        physics=physics,
        geometry=geometry_1,
        surfaces=surfaces,
        display=display_1,
    )
    return_type = 'object'

class mesh_1(NamedObject[mesh_1_child], CreatableNamedObjectMixinOld[mesh_1_child]):
    """
    'mesh' child.
    """
    _version = '222'
    fluent_name = 'mesh'
    _python_name = 'mesh'
    command_names = ['display']
    _child_classes = dict(
        display=display,
    )
    child_object_type = mesh_1_child
    return_type = 'object'

class filled(Boolean):
    """
    'filled' child.
    """
    _version = '222'
    fluent_name = 'filled?'
    _python_name = 'filled'
    return_type = 'object'

class boundary_values(Boolean):
    """
    'boundary_values' child.
    """
    _version = '222'
    fluent_name = 'boundary-values?'
    _python_name = 'boundary_values'
    return_type = 'object'

class contour_lines(Boolean):
    """
    'contour_lines' child.
    """
    _version = '222'
    fluent_name = 'contour-lines?'
    _python_name = 'contour_lines'
    return_type = 'object'

class node_values(Boolean):
    """
    'node_values' child.
    """
    _version = '222'
    fluent_name = 'node-values?'
    _python_name = 'node_values'
    return_type = 'object'

class global_range(Boolean):
    """
    'global_range' child.
    """
    _version = '222'
    fluent_name = 'global-range?'
    _python_name = 'global_range'
    return_type = 'object'

class auto_range_on(Group):
    """
    'auto_range_on' child.
    """
    _version = '222'
    fluent_name = 'auto-range-on'
    _python_name = 'auto_range_on'
    child_names = ['global_range']
    _child_classes = dict(
        global_range=global_range,
    )
    return_type = 'object'

class clip_to_range(Boolean):
    """
    'clip_to_range' child.
    """
    _version = '222'
    fluent_name = 'clip-to-range?'
    _python_name = 'clip_to_range'
    return_type = 'object'

class auto_range_off(Group):
    """
    'auto_range_off' child.
    """
    _version = '222'
    fluent_name = 'auto-range-off'
    _python_name = 'auto_range_off'
    child_names = ['clip_to_range', 'minimum', 'maximum']
    _child_classes = dict(
        clip_to_range=clip_to_range,
        minimum=minimum,
        maximum=maximum,
    )
    return_type = 'object'

class range_option(Group):
    """
    'range_option' child.
    """
    _version = '222'
    fluent_name = 'range-option'
    _python_name = 'range_option'
    child_names = ['option', 'auto_range_on', 'auto_range_off']
    _child_classes = dict(
        option=option,
        auto_range_on=auto_range_on,
        auto_range_off=auto_range_off,
    )
    return_type = 'object'

class smooth(Boolean):
    """
    'smooth' child.
    """
    _version = '222'
    fluent_name = 'smooth'
    _python_name = 'smooth'
    return_type = 'object'

class banded(Group):
    """
    'banded' child.
    """
    _version = '222'
    fluent_name = 'banded'
    _python_name = 'banded'
    return_type = 'object'

class coloring_1(Group):
    """
    'coloring' child.
    """
    _version = '222'
    fluent_name = 'coloring'
    _python_name = 'coloring'
    child_names = ['option', 'smooth', 'banded']
    _child_classes = dict(
        option=option,
        smooth=smooth,
        banded=banded,
    )
    return_type = 'object'

class visible(Boolean):
    """
    'visible' child.
    """
    _version = '222'
    fluent_name = 'visible?'
    _python_name = 'visible'
    return_type = 'object'

class size(Integer):
    """
    'size' child.
    """
    _version = '222'
    fluent_name = 'size'
    _python_name = 'size'
    return_type = 'object'

class color(String, AllowedValuesMixin):
    """
    'color' child.
    """
    _version = '222'
    fluent_name = 'color'
    _python_name = 'color'
    return_type = 'object'

class log_scale(Boolean):
    """
    'log_scale' child.
    """
    _version = '222'
    fluent_name = 'log-scale?'
    _python_name = 'log_scale'
    return_type = 'object'

class format(String, AllowedValuesMixin):
    """
    'format' child.
    """
    _version = '222'
    fluent_name = 'format'
    _python_name = 'format'
    return_type = 'object'

class user_skip(Integer):
    """
    'user_skip' child.
    """
    _version = '222'
    fluent_name = 'user-skip'
    _python_name = 'user_skip'
    return_type = 'object'

class show_all(Boolean):
    """
    'show_all' child.
    """
    _version = '222'
    fluent_name = 'show-all'
    _python_name = 'show_all'
    return_type = 'object'

class position(Integer):
    """
    'position' child.
    """
    _version = '222'
    fluent_name = 'position'
    _python_name = 'position'
    return_type = 'object'

class font_name(String, AllowedValuesMixin):
    """
    'font_name' child.
    """
    _version = '222'
    fluent_name = 'font-name'
    _python_name = 'font_name'
    return_type = 'object'

class font_automatic(Boolean):
    """
    'font_automatic' child.
    """
    _version = '222'
    fluent_name = 'font-automatic'
    _python_name = 'font_automatic'
    return_type = 'object'

class font_size(Real):
    """
    'font_size' child.
    """
    _version = '222'
    fluent_name = 'font-size'
    _python_name = 'font_size'
    return_type = 'object'

class length(Real):
    """
    'length' child.
    """
    _version = '222'
    fluent_name = 'length'
    _python_name = 'length'
    return_type = 'object'

class width(Real):
    """
    'width' child.
    """
    _version = '222'
    fluent_name = 'width'
    _python_name = 'width'
    return_type = 'object'

class color_map(Group):
    """
    'color_map' child.
    """
    _version = '222'
    fluent_name = 'color-map'
    _python_name = 'color_map'
    child_names = ['visible', 'size', 'color', 'log_scale', 'format', 'user_skip', 'show_all', 'position', 'font_name', 'font_automatic', 'font_size', 'length', 'width']
    _child_classes = dict(
        visible=visible,
        size=size,
        color=color,
        log_scale=log_scale,
        format=format,
        user_skip=user_skip,
        show_all=show_all,
        position=position,
        font_name=font_name,
        font_automatic=font_automatic,
        font_size=font_size,
        length=length,
        width=width,
    )
    return_type = 'object'

class draw_mesh(Boolean):
    """
    'draw_mesh' child.
    """
    _version = '222'
    fluent_name = 'draw-mesh?'
    _python_name = 'draw_mesh'
    return_type = 'object'

class mesh_object(String, AllowedValuesMixin):
    """
    'mesh_object' child.
    """
    _version = '222'
    fluent_name = 'mesh-object'
    _python_name = 'mesh_object'
    return_type = 'object'

class contour_child(Group):
    """
    'child_object_type' of contour.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'contour_child'
    child_names = ['name', 'field', 'filled', 'boundary_values', 'contour_lines', 'node_values', 'surfaces_list', 'range_option', 'coloring', 'color_map', 'draw_mesh', 'mesh_object', 'display_state_name', 'physics', 'geometry', 'surfaces']
    command_names = ['display']
    _child_classes = dict(
        name=name,
        field=field,
        filled=filled,
        boundary_values=boundary_values,
        contour_lines=contour_lines,
        node_values=node_values,
        surfaces_list=surfaces_list,
        range_option=range_option,
        coloring=coloring_1,
        color_map=color_map,
        draw_mesh=draw_mesh,
        mesh_object=mesh_object,
        display_state_name=display_state_name,
        physics=physics,
        geometry=geometry_1,
        surfaces=surfaces,
        display=display_1,
    )
    return_type = 'object'

class contour(NamedObject[contour_child], CreatableNamedObjectMixinOld[contour_child]):
    """
    'contour' child.
    """
    _version = '222'
    fluent_name = 'contour'
    _python_name = 'contour'
    command_names = ['display']
    _child_classes = dict(
        display=display,
    )
    child_object_type = contour_child
    return_type = 'object'

class vector_field(String, AllowedValuesMixin):
    """
    'vector_field' child.
    """
    _version = '222'
    fluent_name = 'vector-field'
    _python_name = 'vector_field'
    return_type = 'object'

class auto_scale(Boolean):
    """
    'auto_scale' child.
    """
    _version = '222'
    fluent_name = 'auto-scale?'
    _python_name = 'auto_scale'
    return_type = 'object'

class scale_f(Real):
    """
    'scale_f' child.
    """
    _version = '222'
    fluent_name = 'scale-f'
    _python_name = 'scale_f'
    return_type = 'object'

class scale(Group):
    """
    'scale' child.
    """
    _version = '222'
    fluent_name = 'scale'
    _python_name = 'scale'
    child_names = ['auto_scale', 'scale_f']
    _child_classes = dict(
        auto_scale=auto_scale,
        scale_f=scale_f,
    )
    return_type = 'object'

class style(String, AllowedValuesMixin):
    """
    'style' child.
    """
    _version = '222'
    fluent_name = 'style'
    _python_name = 'style'
    return_type = 'object'

class skip(Integer):
    """
    'skip' child.
    """
    _version = '222'
    fluent_name = 'skip'
    _python_name = 'skip'
    return_type = 'object'

class in_plane(Boolean):
    """
    'in_plane' child.
    """
    _version = '222'
    fluent_name = 'in-plane?'
    _python_name = 'in_plane'
    return_type = 'object'

class fixed_length(Boolean):
    """
    'fixed_length' child.
    """
    _version = '222'
    fluent_name = 'fixed-length?'
    _python_name = 'fixed_length'
    return_type = 'object'

class x_comp(Boolean):
    """
    'x_comp' child.
    """
    _version = '222'
    fluent_name = 'x-comp?'
    _python_name = 'x_comp'
    return_type = 'object'

class y_comp(Boolean):
    """
    'y_comp' child.
    """
    _version = '222'
    fluent_name = 'y-comp?'
    _python_name = 'y_comp'
    return_type = 'object'

class z_comp(Boolean):
    """
    'z_comp' child.
    """
    _version = '222'
    fluent_name = 'z-comp?'
    _python_name = 'z_comp'
    return_type = 'object'

class scale_head(Real):
    """
    'scale_head' child.
    """
    _version = '222'
    fluent_name = 'scale-head'
    _python_name = 'scale_head'
    return_type = 'object'

class vector_opt(Group):
    """
    'vector_opt' child.
    """
    _version = '222'
    fluent_name = 'vector-opt'
    _python_name = 'vector_opt'
    child_names = ['in_plane', 'fixed_length', 'x_comp', 'y_comp', 'z_comp', 'scale_head', 'color']
    _child_classes = dict(
        in_plane=in_plane,
        fixed_length=fixed_length,
        x_comp=x_comp,
        y_comp=y_comp,
        z_comp=z_comp,
        scale_head=scale_head,
        color=color,
    )
    return_type = 'object'

class vector_child(Group):
    """
    'child_object_type' of vector.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'vector_child'
    child_names = ['name', 'field', 'vector_field', 'surfaces_list', 'scale', 'style', 'skip', 'vector_opt', 'range_option', 'color_map', 'draw_mesh', 'mesh_object', 'display_state_name', 'physics', 'geometry', 'surfaces']
    command_names = ['display']
    _child_classes = dict(
        name=name,
        field=field,
        vector_field=vector_field,
        surfaces_list=surfaces_list,
        scale=scale,
        style=style,
        skip=skip,
        vector_opt=vector_opt,
        range_option=range_option,
        color_map=color_map,
        draw_mesh=draw_mesh,
        mesh_object=mesh_object,
        display_state_name=display_state_name,
        physics=physics,
        geometry=geometry_1,
        surfaces=surfaces,
        display=display_1,
    )
    return_type = 'object'

class vector(NamedObject[vector_child], CreatableNamedObjectMixinOld[vector_child]):
    """
    'vector' child.
    """
    _version = '222'
    fluent_name = 'vector'
    _python_name = 'vector'
    command_names = ['display']
    _child_classes = dict(
        display=display,
    )
    child_object_type = vector_child
    return_type = 'object'

class uid(String, AllowedValuesMixin):
    """
    'uid' child.
    """
    _version = '222'
    fluent_name = 'uid'
    _python_name = 'uid'
    return_type = 'object'

class oil_flow(Boolean):
    """
    'oil_flow' child.
    """
    _version = '222'
    fluent_name = 'oil-flow'
    _python_name = 'oil_flow'
    return_type = 'object'

class reverse(Boolean):
    """
    'reverse' child.
    """
    _version = '222'
    fluent_name = 'reverse'
    _python_name = 'reverse'
    return_type = 'object'

class node_values_1(Boolean):
    """
    'node_values' child.
    """
    _version = '222'
    fluent_name = 'node-values'
    _python_name = 'node_values'
    return_type = 'object'

class relative_1(Boolean):
    """
    'relative' child.
    """
    _version = '222'
    fluent_name = 'relative'
    _python_name = 'relative'
    return_type = 'object'

class options_5(Group):
    """
    'options' child.
    """
    _version = '222'
    fluent_name = 'options'
    _python_name = 'options'
    child_names = ['oil_flow', 'reverse', 'node_values', 'relative']
    _child_classes = dict(
        oil_flow=oil_flow,
        reverse=reverse,
        node_values=node_values_1,
        relative=relative_1,
    )
    return_type = 'object'

class auto_range(Group):
    """
    'auto_range' child.
    """
    _version = '222'
    fluent_name = 'auto-range'
    _python_name = 'auto_range'
    return_type = 'object'

class min_value(Real):
    """
    'min_value' child.
    """
    _version = '222'
    fluent_name = 'min-value'
    _python_name = 'min_value'
    return_type = 'object'

class max_value(Real):
    """
    'max_value' child.
    """
    _version = '222'
    fluent_name = 'max-value'
    _python_name = 'max_value'
    return_type = 'object'

class clip_to_range_1(Group):
    """
    'clip_to_range' child.
    """
    _version = '222'
    fluent_name = 'clip-to-range'
    _python_name = 'clip_to_range'
    child_names = ['min_value', 'max_value']
    _child_classes = dict(
        min_value=min_value,
        max_value=max_value,
    )
    return_type = 'object'

class range(Group):
    """
    'range' child.
    """
    _version = '222'
    fluent_name = 'range'
    _python_name = 'range'
    child_names = ['option', 'auto_range', 'clip_to_range']
    _child_classes = dict(
        option=option,
        auto_range=auto_range,
        clip_to_range=clip_to_range_1,
    )
    return_type = 'object'

class line_width(Real):
    """
    'line_width' child.
    """
    _version = '222'
    fluent_name = 'line-width'
    _python_name = 'line_width'
    return_type = 'object'

class arrow_space(Real):
    """
    'arrow_space' child.
    """
    _version = '222'
    fluent_name = 'arrow-space'
    _python_name = 'arrow_space'
    return_type = 'object'

class arrow_scale(Real):
    """
    'arrow_scale' child.
    """
    _version = '222'
    fluent_name = 'arrow-scale'
    _python_name = 'arrow_scale'
    return_type = 'object'

class marker_size(Real):
    """
    'marker_size' child.
    """
    _version = '222'
    fluent_name = 'marker-size'
    _python_name = 'marker_size'
    return_type = 'object'

class sphere_size(Real):
    """
    'sphere_size' child.
    """
    _version = '222'
    fluent_name = 'sphere-size'
    _python_name = 'sphere_size'
    return_type = 'object'

class sphere_lod(Integer):
    """
    'sphere_lod' child.
    """
    _version = '222'
    fluent_name = 'sphere-lod'
    _python_name = 'sphere_lod'
    return_type = 'object'

class radius(Real):
    """
    'radius' child.
    """
    _version = '222'
    fluent_name = 'radius'
    _python_name = 'radius'
    return_type = 'object'

class scalefactor(Real):
    """
    'scalefactor' child.
    """
    _version = '222'
    fluent_name = 'scalefactor'
    _python_name = 'scalefactor'
    return_type = 'object'

class ribbon(Group):
    """
    'ribbon' child.
    """
    _version = '222'
    fluent_name = 'ribbon'
    _python_name = 'ribbon'
    child_names = ['field', 'scalefactor']
    _child_classes = dict(
        field=field,
        scalefactor=scalefactor,
    )
    return_type = 'object'

class style_attribute(Group):
    """
    'style_attribute' child.
    """
    _version = '222'
    fluent_name = 'style-attribute'
    _python_name = 'style_attribute'
    child_names = ['style', 'line_width', 'arrow_space', 'arrow_scale', 'marker_size', 'sphere_size', 'sphere_lod', 'radius', 'ribbon']
    _child_classes = dict(
        style=style,
        line_width=line_width,
        arrow_space=arrow_space,
        arrow_scale=arrow_scale,
        marker_size=marker_size,
        sphere_size=sphere_size,
        sphere_lod=sphere_lod,
        radius=radius,
        ribbon=ribbon,
    )
    return_type = 'object'

class step_size(Real):
    """
    'step_size' child.
    """
    _version = '222'
    fluent_name = 'step-size'
    _python_name = 'step_size'
    return_type = 'object'

class tolerance(Real):
    """
    'tolerance' child.
    """
    _version = '222'
    fluent_name = 'tolerance'
    _python_name = 'tolerance'
    return_type = 'object'

class accuracy_control(Group):
    """
    'accuracy_control' child.
    """
    _version = '222'
    fluent_name = 'accuracy-control'
    _python_name = 'accuracy_control'
    child_names = ['option', 'step_size', 'tolerance']
    _child_classes = dict(
        option=option,
        step_size=step_size,
        tolerance=tolerance,
    )
    return_type = 'object'

class x_axis_function(String, AllowedValuesMixin):
    """
    'x_axis_function' child.
    """
    _version = '222'
    fluent_name = 'x-axis-function'
    _python_name = 'x_axis_function'
    return_type = 'object'

class plot(Group):
    """
    'plot' child.
    """
    _version = '222'
    fluent_name = 'plot'
    _python_name = 'plot'
    child_names = ['x_axis_function', 'enabled']
    _child_classes = dict(
        x_axis_function=x_axis_function,
        enabled=enabled_2,
    )
    return_type = 'object'

class step(Integer):
    """
    'step' child.
    """
    _version = '222'
    fluent_name = 'step'
    _python_name = 'step'
    return_type = 'object'

class coarsen(Integer):
    """
    'coarsen' child.
    """
    _version = '222'
    fluent_name = 'coarsen'
    _python_name = 'coarsen'
    return_type = 'object'

class onzone(StringList, AllowedValuesMixin):
    """
    'onzone' child.
    """
    _version = '222'
    fluent_name = 'onzone'
    _python_name = 'onzone'
    return_type = 'object'

class velocity_domain(String, AllowedValuesMixin):
    """
    'velocity_domain' child.
    """
    _version = '222'
    fluent_name = 'velocity-domain'
    _python_name = 'velocity_domain'
    return_type = 'object'

class pathlines_child(Group):
    """
    'child_object_type' of pathlines.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'pathlines_child'
    child_names = ['name', 'uid', 'options', 'range', 'style_attribute', 'accuracy_control', 'plot', 'step', 'skip', 'coarsen', 'onzone', 'field', 'surfaces_list', 'velocity_domain', 'color_map', 'draw_mesh', 'mesh_object', 'display_state_name', 'physics', 'geometry', 'surfaces']
    command_names = ['display']
    _child_classes = dict(
        name=name,
        uid=uid,
        options=options_5,
        range=range,
        style_attribute=style_attribute,
        accuracy_control=accuracy_control,
        plot=plot,
        step=step,
        skip=skip,
        coarsen=coarsen,
        onzone=onzone,
        field=field,
        surfaces_list=surfaces_list,
        velocity_domain=velocity_domain,
        color_map=color_map,
        draw_mesh=draw_mesh,
        mesh_object=mesh_object,
        display_state_name=display_state_name,
        physics=physics,
        geometry=geometry_1,
        surfaces=surfaces,
        display=display_1,
    )
    return_type = 'object'

class pathlines(NamedObject[pathlines_child], CreatableNamedObjectMixinOld[pathlines_child]):
    """
    'pathlines' child.
    """
    _version = '222'
    fluent_name = 'pathlines'
    _python_name = 'pathlines'
    command_names = ['display']
    _child_classes = dict(
        display=display,
    )
    child_object_type = pathlines_child
    return_type = 'object'

class options_6(Group):
    """
    'options' child.
    """
    _version = '222'
    fluent_name = 'options'
    _python_name = 'options'
    child_names = ['node_values']
    _child_classes = dict(
        node_values=node_values_1,
    )
    return_type = 'object'

class inside(Boolean):
    """
    'inside' child.
    """
    _version = '222'
    fluent_name = 'inside'
    _python_name = 'inside'
    return_type = 'object'

class outside(Boolean):
    """
    'outside' child.
    """
    _version = '222'
    fluent_name = 'outside'
    _python_name = 'outside'
    return_type = 'object'

class options_7(Group):
    """
    'options' child.
    """
    _version = '222'
    fluent_name = 'options'
    _python_name = 'options'
    child_names = ['option', 'inside', 'outside']
    _child_classes = dict(
        option=option,
        inside=inside,
        outside=outside,
    )
    return_type = 'object'

class filter_minimum(Real):
    """
    'filter_minimum' child.
    """
    _version = '222'
    fluent_name = 'filter-minimum'
    _python_name = 'filter_minimum'
    return_type = 'object'

class filter_maximum(Real):
    """
    'filter_maximum' child.
    """
    _version = '222'
    fluent_name = 'filter-maximum'
    _python_name = 'filter_maximum'
    return_type = 'object'

class filter_settings(Group):
    """
    'filter_settings' child.
    """
    _version = '222'
    fluent_name = 'filter-settings'
    _python_name = 'filter_settings'
    child_names = ['field', 'options', 'enabled', 'filter_minimum', 'filter_maximum']
    _child_classes = dict(
        field=field,
        options=options_7,
        enabled=enabled_2,
        filter_minimum=filter_minimum,
        filter_maximum=filter_maximum,
    )
    return_type = 'object'

class ribbon_settings(Group):
    """
    'ribbon_settings' child.
    """
    _version = '222'
    fluent_name = 'ribbon-settings'
    _python_name = 'ribbon_settings'
    child_names = ['field', 'scalefactor']
    _child_classes = dict(
        field=field,
        scalefactor=scalefactor,
    )
    return_type = 'object'

class scale_1(Real):
    """
    'scale' child.
    """
    _version = '222'
    fluent_name = 'scale'
    _python_name = 'scale'
    return_type = 'object'

class diameter(Real):
    """
    'diameter' child.
    """
    _version = '222'
    fluent_name = 'diameter'
    _python_name = 'diameter'
    return_type = 'object'

class constant_1(Group):
    """
    'constant' child.
    """
    _version = '222'
    fluent_name = 'constant'
    _python_name = 'constant'
    child_names = ['diameter']
    _child_classes = dict(
        diameter=diameter,
    )
    return_type = 'object'

class size_by(String, AllowedValuesMixin):
    """
    'size_by' child.
    """
    _version = '222'
    fluent_name = 'size-by'
    _python_name = 'size_by'
    return_type = 'object'

class variable(Group):
    """
    'variable' child.
    """
    _version = '222'
    fluent_name = 'variable'
    _python_name = 'variable'
    child_names = ['size_by', 'range']
    _child_classes = dict(
        size_by=size_by,
        range=range,
    )
    return_type = 'object'

class options_8(Group):
    """
    'options' child.
    """
    _version = '222'
    fluent_name = 'options'
    _python_name = 'options'
    child_names = ['option', 'constant', 'variable']
    _child_classes = dict(
        option=option,
        constant=constant_1,
        variable=variable,
    )
    return_type = 'object'

class sphere_settings(Group):
    """
    'sphere_settings' child.
    """
    _version = '222'
    fluent_name = 'sphere-settings'
    _python_name = 'sphere_settings'
    child_names = ['scale', 'sphere_lod', 'options']
    _child_classes = dict(
        scale=scale_1,
        sphere_lod=sphere_lod,
        options=options_8,
    )
    return_type = 'object'

class style_attribute_1(Group):
    """
    'style_attribute' child.
    """
    _version = '222'
    fluent_name = 'style-attribute'
    _python_name = 'style_attribute'
    child_names = ['style', 'line_width', 'arrow_space', 'arrow_scale', 'marker_size', 'sphere_size', 'sphere_lod', 'radius', 'ribbon_settings', 'sphere_settings']
    _child_classes = dict(
        style=style,
        line_width=line_width,
        arrow_space=arrow_space,
        arrow_scale=arrow_scale,
        marker_size=marker_size,
        sphere_size=sphere_size,
        sphere_lod=sphere_lod,
        radius=radius,
        ribbon_settings=ribbon_settings,
        sphere_settings=sphere_settings,
    )
    return_type = 'object'

class constant_length(Real):
    """
    'constant_length' child.
    """
    _version = '222'
    fluent_name = 'constant-length'
    _python_name = 'constant_length'
    return_type = 'object'

class variable_length(String, AllowedValuesMixin):
    """
    'variable_length' child.
    """
    _version = '222'
    fluent_name = 'variable-length'
    _python_name = 'variable_length'
    return_type = 'object'

class vector_length(Group):
    """
    'vector_length' child.
    """
    _version = '222'
    fluent_name = 'vector-length'
    _python_name = 'vector_length'
    child_names = ['option', 'constant_length', 'variable_length']
    _child_classes = dict(
        option=option,
        constant_length=constant_length,
        variable_length=variable_length,
    )
    return_type = 'object'

class constant_color(Group):
    """
    'constant_color' child.
    """
    _version = '222'
    fluent_name = 'constant-color'
    _python_name = 'constant_color'
    child_names = ['enabled', 'color']
    _child_classes = dict(
        enabled=enabled_2,
        color=color,
    )
    return_type = 'object'

class vector_of(String, AllowedValuesMixin):
    """
    'vector_of' child.
    """
    _version = '222'
    fluent_name = 'vector-of'
    _python_name = 'vector_of'
    return_type = 'object'

class length_to_head_ratio(Real):
    """
    'length_to_head_ratio' child.
    """
    _version = '222'
    fluent_name = 'length-to-head-ratio'
    _python_name = 'length_to_head_ratio'
    return_type = 'object'

class vector_settings(Group):
    """
    'vector_settings' child.
    """
    _version = '222'
    fluent_name = 'vector-settings'
    _python_name = 'vector_settings'
    child_names = ['style', 'vector_length', 'constant_color', 'vector_of', 'scale', 'length_to_head_ratio']
    _child_classes = dict(
        style=style,
        vector_length=vector_length,
        constant_color=constant_color,
        vector_of=vector_of,
        scale=scale_1,
        length_to_head_ratio=length_to_head_ratio,
    )
    return_type = 'object'

class stream_id(Integer):
    """
    'stream_id' child.
    """
    _version = '222'
    fluent_name = 'stream-id'
    _python_name = 'stream_id'
    return_type = 'object'

class track_single_particle_stream(Group):
    """
    'track_single_particle_stream' child.
    """
    _version = '222'
    fluent_name = 'track-single-particle-stream'
    _python_name = 'track_single_particle_stream'
    child_names = ['enabled', 'stream_id']
    _child_classes = dict(
        enabled=enabled_2,
        stream_id=stream_id,
    )
    return_type = 'object'

class injections_list(StringList, AllowedValuesMixin):
    """
    'injections_list' child.
    """
    _version = '222'
    fluent_name = 'injections-list'
    _python_name = 'injections_list'
    return_type = 'object'

class free_stream_particles(Boolean):
    """
    'free_stream_particles' child.
    """
    _version = '222'
    fluent_name = 'free-stream-particles?'
    _python_name = 'free_stream_particles'
    return_type = 'object'

class wall_film_particles(Boolean):
    """
    'wall_film_particles' child.
    """
    _version = '222'
    fluent_name = 'wall-film-particles?'
    _python_name = 'wall_film_particles'
    return_type = 'object'

class track_pdf_particles(Boolean):
    """
    'track_pdf_particles' child.
    """
    _version = '222'
    fluent_name = 'track-pdf-particles?'
    _python_name = 'track_pdf_particles'
    return_type = 'object'

class particle_tracks_child(Group):
    """
    'child_object_type' of particle_tracks.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'particle_tracks_child'
    child_names = ['name', 'uid', 'options', 'filter_settings', 'range', 'style_attribute', 'vector_settings', 'plot', 'track_single_particle_stream', 'skip', 'coarsen', 'field', 'injections_list', 'free_stream_particles', 'wall_film_particles', 'track_pdf_particles', 'color_map', 'draw_mesh', 'mesh_object', 'display_state_name']
    command_names = ['display']
    _child_classes = dict(
        name=name,
        uid=uid,
        options=options_6,
        filter_settings=filter_settings,
        range=range,
        style_attribute=style_attribute_1,
        vector_settings=vector_settings,
        plot=plot,
        track_single_particle_stream=track_single_particle_stream,
        skip=skip,
        coarsen=coarsen,
        field=field,
        injections_list=injections_list,
        free_stream_particles=free_stream_particles,
        wall_film_particles=wall_film_particles,
        track_pdf_particles=track_pdf_particles,
        color_map=color_map,
        draw_mesh=draw_mesh,
        mesh_object=mesh_object,
        display_state_name=display_state_name,
        display=display_1,
    )
    return_type = 'object'

class particle_tracks(NamedObject[particle_tracks_child], CreatableNamedObjectMixinOld[particle_tracks_child]):
    """
    'particle_tracks' child.
    """
    _version = '222'
    fluent_name = 'particle-tracks'
    _python_name = 'particle_tracks'
    command_names = ['display']
    _child_classes = dict(
        display=display,
    )
    child_object_type = particle_tracks_child
    return_type = 'object'

class lic_color_by_field(Boolean):
    """
    'lic_color_by_field' child.
    """
    _version = '222'
    fluent_name = 'lic-color-by-field?'
    _python_name = 'lic_color_by_field'
    return_type = 'object'

class lic_color(String, AllowedValuesMixin):
    """
    'lic_color' child.
    """
    _version = '222'
    fluent_name = 'lic-color'
    _python_name = 'lic_color'
    return_type = 'object'

class lic_oriented(Boolean):
    """
    'lic_oriented' child.
    """
    _version = '222'
    fluent_name = 'lic-oriented?'
    _python_name = 'lic_oriented'
    return_type = 'object'

class lic_normalize(Boolean):
    """
    'lic_normalize' child.
    """
    _version = '222'
    fluent_name = 'lic-normalize?'
    _python_name = 'lic_normalize'
    return_type = 'object'

class lic_pixel_interpolation(Boolean):
    """
    'lic_pixel_interpolation' child.
    """
    _version = '222'
    fluent_name = 'lic-pixel-interpolation?'
    _python_name = 'lic_pixel_interpolation'
    return_type = 'object'

class lic_max_steps(Integer):
    """
    'lic_max_steps' child.
    """
    _version = '222'
    fluent_name = 'lic-max-steps'
    _python_name = 'lic_max_steps'
    return_type = 'object'

class texture_spacing(Integer):
    """
    'texture_spacing' child.
    """
    _version = '222'
    fluent_name = 'texture-spacing'
    _python_name = 'texture_spacing'
    return_type = 'object'

class texture_size(Integer):
    """
    'texture_size' child.
    """
    _version = '222'
    fluent_name = 'texture-size'
    _python_name = 'texture_size'
    return_type = 'object'

class lic_intensity_factor(Integer):
    """
    'lic_intensity_factor' child.
    """
    _version = '222'
    fluent_name = 'lic-intensity-factor'
    _python_name = 'lic_intensity_factor'
    return_type = 'object'

class lic_image_filter(String, AllowedValuesMixin):
    """
    'lic_image_filter' child.
    """
    _version = '222'
    fluent_name = 'lic-image-filter'
    _python_name = 'lic_image_filter'
    return_type = 'object'

class lic_intensity_alpha(Boolean):
    """
    'lic_intensity_alpha' child.
    """
    _version = '222'
    fluent_name = 'lic-intensity-alpha?'
    _python_name = 'lic_intensity_alpha'
    return_type = 'object'

class lic_fast(Boolean):
    """
    'lic_fast' child.
    """
    _version = '222'
    fluent_name = 'lic-fast?'
    _python_name = 'lic_fast'
    return_type = 'object'

class gray_scale(Boolean):
    """
    'gray_scale' child.
    """
    _version = '222'
    fluent_name = 'gray-scale?'
    _python_name = 'gray_scale'
    return_type = 'object'

class image_to_display(String, AllowedValuesMixin):
    """
    'image_to_display' child.
    """
    _version = '222'
    fluent_name = 'image-to-display'
    _python_name = 'image_to_display'
    return_type = 'object'

class lic_child(Group):
    """
    'child_object_type' of lic.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'lic_child'
    child_names = ['name', 'field', 'vector_field', 'surfaces_list', 'lic_color_by_field', 'lic_color', 'lic_oriented', 'lic_normalize', 'lic_pixel_interpolation', 'lic_max_steps', 'texture_spacing', 'texture_size', 'lic_intensity_factor', 'lic_image_filter', 'lic_intensity_alpha', 'lic_fast', 'gray_scale', 'image_to_display', 'range_option', 'color_map', 'draw_mesh', 'mesh_object', 'display_state_name']
    command_names = ['display']
    _child_classes = dict(
        name=name,
        field=field,
        vector_field=vector_field,
        surfaces_list=surfaces_list,
        lic_color_by_field=lic_color_by_field,
        lic_color=lic_color,
        lic_oriented=lic_oriented,
        lic_normalize=lic_normalize,
        lic_pixel_interpolation=lic_pixel_interpolation,
        lic_max_steps=lic_max_steps,
        texture_spacing=texture_spacing,
        texture_size=texture_size,
        lic_intensity_factor=lic_intensity_factor,
        lic_image_filter=lic_image_filter,
        lic_intensity_alpha=lic_intensity_alpha,
        lic_fast=lic_fast,
        gray_scale=gray_scale,
        image_to_display=image_to_display,
        range_option=range_option,
        color_map=color_map,
        draw_mesh=draw_mesh,
        mesh_object=mesh_object,
        display_state_name=display_state_name,
        display=display_1,
    )
    return_type = 'object'

class lic(NamedObject[lic_child], CreatableNamedObjectMixinOld[lic_child]):
    """
    'lic' child.
    """
    _version = '222'
    fluent_name = 'lic'
    _python_name = 'lic'
    command_names = ['display']
    _child_classes = dict(
        display=display,
    )
    child_object_type = lic_child
    return_type = 'object'

class color_mode(String, AllowedValuesMixin):
    """
    'color_mode' child.
    """
    _version = '222'
    fluent_name = 'color-mode'
    _python_name = 'color_mode'
    return_type = 'object'

class invert_background(Boolean):
    """
    'invert_background' child.
    """
    _version = '222'
    fluent_name = 'invert-background?'
    _python_name = 'invert_background'
    return_type = 'object'

class hardcopy_format(String, AllowedValuesMixin):
    """
    Hardcopy file format.
    """
    _version = '222'
    fluent_name = 'hardcopy-format'
    _python_name = 'hardcopy_format'
    return_type = 'object'

class hardcopy_options(String):
    """
    'hardcopy_options' child.
    """
    _version = '222'
    fluent_name = 'hardcopy-options'
    _python_name = 'hardcopy_options'
    return_type = 'object'

class window_dump_cmd(String):
    """
    'window_dump_cmd' child.
    """
    _version = '222'
    fluent_name = 'window-dump-cmd'
    _python_name = 'window_dump_cmd'
    return_type = 'object'

class post_format(String, AllowedValuesMixin):
    """
    Produce PostScript output for hardcopies.
    """
    _version = '222'
    fluent_name = 'post-format'
    _python_name = 'post_format'
    return_type = 'object'

class current_driver(Command):
    """
    'current_driver' command.
    """
    _version = '222'
    fluent_name = 'current-driver'
    _python_name = 'current_driver'
    return_type = 'object'

class driver_options(Group):
    """
    'driver_options' child.
    """
    _version = '222'
    fluent_name = 'driver-options'
    _python_name = 'driver_options'
    child_names = ['hardcopy_format', 'hardcopy_options', 'window_dump_cmd', 'post_format']
    command_names = ['current_driver']
    _child_classes = dict(
        hardcopy_format=hardcopy_format,
        hardcopy_options=hardcopy_options,
        window_dump_cmd=window_dump_cmd,
        post_format=post_format,
        current_driver=current_driver,
    )
    return_type = 'object'

class standard_resolution(String, AllowedValuesMixin):
    """
    From pre-defined resolution list.
    """
    _version = '222'
    fluent_name = 'standard-resolution'
    _python_name = 'standard_resolution'
    return_type = 'object'

class jpeg_hardcopy_quality(Integer):
    """
    0  : Saves lowest quality jpeg image, but with the least file size.
    100: Saves highest quality jpeg image, but with the maximum file size.
    """
    _version = '222'
    fluent_name = 'jpeg-hardcopy-quality'
    _python_name = 'jpeg_hardcopy_quality'
    return_type = 'object'

class landscape(Boolean):
    """
    'landscape' child.
    """
    _version = '222'
    fluent_name = 'landscape?'
    _python_name = 'landscape'
    return_type = 'object'

class x_resolution(Integer):
    """
    'x_resolution' child.
    """
    _version = '222'
    fluent_name = 'x-resolution'
    _python_name = 'x_resolution'
    return_type = 'object'

class y_resolution(Integer):
    """
    'y_resolution' child.
    """
    _version = '222'
    fluent_name = 'y-resolution'
    _python_name = 'y_resolution'
    return_type = 'object'

class dpi(Integer):
    """
    'dpi' child.
    """
    _version = '222'
    fluent_name = 'dpi'
    _python_name = 'dpi'
    return_type = 'object'

class use_window_resolution(Boolean):
    """
    Use the currently active window's resolution for hardcopy (ignores the x-resolution and y-resolution in this case).
    """
    _version = '222'
    fluent_name = 'use-window-resolution?'
    _python_name = 'use_window_resolution'
    return_type = 'object'

class list_color_mode(Command):
    """
    'list_color_mode' command.
    """
    _version = '222'
    fluent_name = 'list-color-mode'
    _python_name = 'list_color_mode'
    return_type = 'object'

class preview(Command):
    """
    Display a preview image of a hardcopy.
    """
    _version = '222'
    fluent_name = 'preview'
    _python_name = 'preview'
    return_type = 'object'

class picture_options(Group):
    """
    'picture_options' child.
    """
    _version = '222'
    fluent_name = 'picture-options'
    _python_name = 'picture_options'
    child_names = ['color_mode', 'invert_background', 'driver_options', 'standard_resolution', 'jpeg_hardcopy_quality', 'landscape', 'x_resolution', 'y_resolution', 'dpi', 'use_window_resolution']
    command_names = ['list_color_mode', 'preview']
    _child_classes = dict(
        color_mode=color_mode,
        invert_background=invert_background,
        driver_options=driver_options,
        standard_resolution=standard_resolution,
        jpeg_hardcopy_quality=jpeg_hardcopy_quality,
        landscape=landscape,
        x_resolution=x_resolution,
        y_resolution=y_resolution,
        dpi=dpi,
        use_window_resolution=use_window_resolution,
        list_color_mode=list_color_mode,
        preview=preview,
    )
    return_type = 'object'

class right(Real):
    """
    'right' child.
    """
    _version = '222'
    fluent_name = 'right'
    _python_name = 'right'
    return_type = 'object'

class up(Real):
    """
    'up' child.
    """
    _version = '222'
    fluent_name = 'up'
    _python_name = 'up'
    return_type = 'object'

class in_(Real):
    """
    'in' child.
    """
    _version = '222'
    fluent_name = 'in'
    _python_name = 'in_'
    return_type = 'object'

class dolly(Command):
    """
    Adjust the camera position and target.
    
    Parameters
    ----------
        right : real
            'right' child.
        up : real
            'up' child.
        in_ : real
            'in' child.
    """
    _version = '222'
    fluent_name = 'dolly'
    _python_name = 'dolly'
    argument_names = ['right', 'up', 'in_']
    _child_classes = dict(
        right=right,
        up=up,
        in_=in_,
    )
    return_type = 'object'

class height(Real):
    """
    'height' child.
    """
    _version = '222'
    fluent_name = 'height'
    _python_name = 'height'
    return_type = 'object'

class field_1(Command):
    """
    Set the field of view (width and height).
    
    Parameters
    ----------
        width : real
            'width' child.
        height : real
            'height' child.
    """
    _version = '222'
    fluent_name = 'field'
    _python_name = 'field'
    argument_names = ['width', 'height']
    _child_classes = dict(
        width=width,
        height=height,
    )
    return_type = 'object'

class orbit(Command):
    """
    Adjust the camera position without modifying the target.
    
    Parameters
    ----------
        right : real
            'right' child.
        up : real
            'up' child.
    """
    _version = '222'
    fluent_name = 'orbit'
    _python_name = 'orbit'
    argument_names = ['right', 'up']
    _child_classes = dict(
        right=right,
        up=up,
    )
    return_type = 'object'

class pan(Command):
    """
    Adjust the camera position without modifying the position.
    
    Parameters
    ----------
        right : real
            'right' child.
        up : real
            'up' child.
    """
    _version = '222'
    fluent_name = 'pan'
    _python_name = 'pan'
    argument_names = ['right', 'up']
    _child_classes = dict(
        right=right,
        up=up,
    )
    return_type = 'object'

class xyz(RealList):
    """
    'xyz' child.
    """
    _version = '222'
    fluent_name = 'xyz'
    _python_name = 'xyz'
    return_type = 'object'

class position_1(Command):
    """
    Set the camera position.
    
    Parameters
    ----------
        xyz : List
            'xyz' child.
    """
    _version = '222'
    fluent_name = 'position'
    _python_name = 'position'
    argument_names = ['xyz']
    _child_classes = dict(
        xyz=xyz,
    )
    return_type = 'object'

class projection(Command):
    """
    Set the camera projection.
    
    Parameters
    ----------
        type : str
            'type' child.
    """
    _version = '222'
    fluent_name = 'projection'
    _python_name = 'projection'
    argument_names = ['type']
    _child_classes = dict(
        type=type_1,
    )
    return_type = 'object'

class counter_clockwise(Real):
    """
    'counter_clockwise' child.
    """
    _version = '222'
    fluent_name = 'counter-clockwise'
    _python_name = 'counter_clockwise'
    return_type = 'object'

class roll(Command):
    """
    Adjust the camera up-vector.
    
    Parameters
    ----------
        counter_clockwise : real
            'counter_clockwise' child.
    """
    _version = '222'
    fluent_name = 'roll'
    _python_name = 'roll'
    argument_names = ['counter_clockwise']
    _child_classes = dict(
        counter_clockwise=counter_clockwise,
    )
    return_type = 'object'

class target(Command):
    """
    Set the point to be the center of the camera view.
    
    Parameters
    ----------
        xyz : List
            'xyz' child.
    """
    _version = '222'
    fluent_name = 'target'
    _python_name = 'target'
    argument_names = ['xyz']
    _child_classes = dict(
        xyz=xyz,
    )
    return_type = 'object'

class up_vector(Command):
    """
    Set the camera up-vector.
    
    Parameters
    ----------
        xyz : List
            'xyz' child.
    """
    _version = '222'
    fluent_name = 'up-vector'
    _python_name = 'up_vector'
    argument_names = ['xyz']
    _child_classes = dict(
        xyz=xyz,
    )
    return_type = 'object'

class factor(Real):
    """
    'factor' child.
    """
    _version = '222'
    fluent_name = 'factor'
    _python_name = 'factor'
    return_type = 'object'

class zoom(Command):
    """
    Adjust the camera field of view.
    
    Parameters
    ----------
        factor : real
            'factor' child.
    """
    _version = '222'
    fluent_name = 'zoom'
    _python_name = 'zoom'
    argument_names = ['factor']
    _child_classes = dict(
        factor=factor,
    )
    return_type = 'object'

class camera(Group):
    """
    'camera' child.
    """
    _version = '222'
    fluent_name = 'camera'
    _python_name = 'camera'
    command_names = ['dolly', 'field', 'orbit', 'pan', 'position', 'projection', 'roll', 'target', 'up_vector', 'zoom']
    _child_classes = dict(
        dolly=dolly,
        field=field_1,
        orbit=orbit,
        pan=pan,
        position=position_1,
        projection=projection,
        roll=roll,
        target=target,
        up_vector=up_vector,
        zoom=zoom,
    )
    return_type = 'object'

class list(Command):
    """
    'list' command.
    """
    _version = '222'
    fluent_name = 'list'
    _python_name = 'list'
    return_type = 'object'

class state_name(String, AllowedValuesMixin):
    """
    'state_name' child.
    """
    _version = '222'
    fluent_name = 'state-name'
    _python_name = 'state_name'
    return_type = 'object'

class use_active(Command):
    """
    'use_active' command.
    """
    _version = '222'
    fluent_name = 'use-active'
    _python_name = 'use_active'
    argument_names = ['state_name']
    _child_classes = dict(
        state_name=state_name,
    )
    return_type = 'object'

class restore_state(Command):
    """
    Apply a display state to the active window.
    
    Parameters
    ----------
        state_name : str
            'state_name' child.
    """
    _version = '222'
    fluent_name = 'restore-state'
    _python_name = 'restore_state'
    argument_names = ['state_name']
    _child_classes = dict(
        state_name=state_name,
    )
    return_type = 'object'

class copy(Command):
    """
    Create a new display state with settings copied from an existing display state.
    
    Parameters
    ----------
        state_name : str
            'state_name' child.
    """
    _version = '222'
    fluent_name = 'copy'
    _python_name = 'copy'
    argument_names = ['state_name']
    _child_classes = dict(
        state_name=state_name,
    )
    return_type = 'object'

class read_1(Command):
    """
    Read display states from a file.
    
    Parameters
    ----------
        file_name : str
            'file_name' child.
    """
    _version = '222'
    fluent_name = 'read'
    _python_name = 'read'
    argument_names = ['file_name']
    _child_classes = dict(
        file_name=file_name,
    )
    return_type = 'object'

class state_name_1(StringList, AllowedValuesMixin):
    """
    'state_name' child.
    """
    _version = '222'
    fluent_name = 'state-name'
    _python_name = 'state_name'
    return_type = 'object'

class write_1(Command):
    """
    Write display states to a file.
    
    Parameters
    ----------
        file_name : str
            'file_name' child.
        state_name : List
            'state_name' child.
    """
    _version = '222'
    fluent_name = 'write'
    _python_name = 'write'
    argument_names = ['file_name', 'state_name']
    _child_classes = dict(
        file_name=file_name,
        state_name=state_name_1,
    )
    return_type = 'object'

class front_faces_transparent(String, AllowedValuesMixin):
    """
    'front_faces_transparent' child.
    """
    _version = '222'
    fluent_name = 'front-faces-transparent'
    _python_name = 'front_faces_transparent'
    return_type = 'object'

class projection_1(String, AllowedValuesMixin):
    """
    'projection' child.
    """
    _version = '222'
    fluent_name = 'projection'
    _python_name = 'projection'
    return_type = 'object'

class axes(String, AllowedValuesMixin):
    """
    'axes' child.
    """
    _version = '222'
    fluent_name = 'axes'
    _python_name = 'axes'
    return_type = 'object'

class ruler(String, AllowedValuesMixin):
    """
    'ruler' child.
    """
    _version = '222'
    fluent_name = 'ruler'
    _python_name = 'ruler'
    return_type = 'object'

class title(String, AllowedValuesMixin):
    """
    'title' child.
    """
    _version = '222'
    fluent_name = 'title'
    _python_name = 'title'
    return_type = 'object'

class boundary_marker(String, AllowedValuesMixin):
    """
    'boundary_marker' child.
    """
    _version = '222'
    fluent_name = 'boundary-marker'
    _python_name = 'boundary_marker'
    return_type = 'object'

class anti_aliasing(String, AllowedValuesMixin):
    """
    'anti_aliasing' child.
    """
    _version = '222'
    fluent_name = 'anti-aliasing'
    _python_name = 'anti_aliasing'
    return_type = 'object'

class reflections(String, AllowedValuesMixin):
    """
    'reflections' child.
    """
    _version = '222'
    fluent_name = 'reflections'
    _python_name = 'reflections'
    return_type = 'object'

class static_shadows(String, AllowedValuesMixin):
    """
    'static_shadows' child.
    """
    _version = '222'
    fluent_name = 'static-shadows'
    _python_name = 'static_shadows'
    return_type = 'object'

class dynamic_shadows(String, AllowedValuesMixin):
    """
    'dynamic_shadows' child.
    """
    _version = '222'
    fluent_name = 'dynamic-shadows'
    _python_name = 'dynamic_shadows'
    return_type = 'object'

class grid_plane(String, AllowedValuesMixin):
    """
    'grid_plane' child.
    """
    _version = '222'
    fluent_name = 'grid-plane'
    _python_name = 'grid_plane'
    return_type = 'object'

class headlights(String, AllowedValuesMixin):
    """
    'headlights' child.
    """
    _version = '222'
    fluent_name = 'headlights'
    _python_name = 'headlights'
    return_type = 'object'

class lighting(String, AllowedValuesMixin):
    """
    'lighting' child.
    """
    _version = '222'
    fluent_name = 'lighting'
    _python_name = 'lighting'
    return_type = 'object'

class view_name(String, AllowedValuesMixin):
    """
    'view_name' child.
    """
    _version = '222'
    fluent_name = 'view-name'
    _python_name = 'view_name'
    return_type = 'object'

class display_states_child(Group):
    """
    'child_object_type' of display_states.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'display_states_child'
    child_names = ['front_faces_transparent', 'projection', 'axes', 'ruler', 'title', 'boundary_marker', 'anti_aliasing', 'reflections', 'static_shadows', 'dynamic_shadows', 'grid_plane', 'headlights', 'lighting', 'view_name']
    _child_classes = dict(
        front_faces_transparent=front_faces_transparent,
        projection=projection_1,
        axes=axes,
        ruler=ruler,
        title=title,
        boundary_marker=boundary_marker,
        anti_aliasing=anti_aliasing,
        reflections=reflections,
        static_shadows=static_shadows,
        dynamic_shadows=dynamic_shadows,
        grid_plane=grid_plane,
        headlights=headlights,
        lighting=lighting,
        view_name=view_name,
    )
    return_type = 'object'

class display_states(NamedObject[display_states_child], CreatableNamedObjectMixinOld[display_states_child]):
    """
    'display_states' child.
    """
    _version = '222'
    fluent_name = 'display-states'
    _python_name = 'display_states'
    command_names = ['list', 'use_active', 'restore_state', 'copy', 'read', 'write']
    _child_classes = dict(
        list=list,
        use_active=use_active,
        restore_state=restore_state,
        copy=copy,
        read=read_1,
        write=write_1,
    )
    child_object_type = display_states_child
    return_type = 'object'

class save_picture(Command):
    """
    'save_picture' command.
    """
    _version = '222'
    fluent_name = 'save-picture'
    _python_name = 'save_picture'
    argument_names = ['file_name']
    _child_classes = dict(
        file_name=file_name,
    )
    return_type = 'object'

class auto_scale_1(Command):
    """
    'auto_scale' command.
    """
    _version = '222'
    fluent_name = 'auto-scale'
    _python_name = 'auto_scale'
    return_type = 'object'

class reset_to_default_view(Command):
    """
    Reset view to front and center.
    """
    _version = '222'
    fluent_name = 'reset-to-default-view'
    _python_name = 'reset_to_default_view'
    return_type = 'object'

class delete_view(Command):
    """
    Remove a view from the list.
    
    Parameters
    ----------
        view_name : str
            'view_name' child.
    """
    _version = '222'
    fluent_name = 'delete-view'
    _python_name = 'delete_view'
    argument_names = ['view_name']
    _child_classes = dict(
        view_name=view_name,
    )
    return_type = 'object'

class last_view(Command):
    """
    Return to the camera position before the last manipulation.
    """
    _version = '222'
    fluent_name = 'last-view'
    _python_name = 'last_view'
    return_type = 'object'

class next_view(Command):
    """
    Return to the camera position after the current position in the stack.
    """
    _version = '222'
    fluent_name = 'next-view'
    _python_name = 'next_view'
    return_type = 'object'

class restore_view(Command):
    """
    Use a saved view.
    
    Parameters
    ----------
        view_name : str
            'view_name' child.
    """
    _version = '222'
    fluent_name = 'restore-view'
    _python_name = 'restore_view'
    argument_names = ['view_name']
    _child_classes = dict(
        view_name=view_name,
    )
    return_type = 'object'

class filename(Filename):
    """
    'filename' child.
    """
    _version = '222'
    fluent_name = 'filename'
    _python_name = 'filename'
    return_type = 'object'

class read_views(Command):
    """
    Read views from a view file.
    
    Parameters
    ----------
        filename : str
            'filename' child.
    """
    _version = '222'
    fluent_name = 'read-views'
    _python_name = 'read_views'
    argument_names = ['filename']
    _child_classes = dict(
        filename=filename,
    )
    return_type = 'object'

class view_name_1(String):
    """
    'view_name' child.
    """
    _version = '222'
    fluent_name = 'view-name'
    _python_name = 'view_name'
    return_type = 'object'

class save_view(Command):
    """
    Save the current view to the view list.
    
    Parameters
    ----------
        view_name : str
            'view_name' child.
    """
    _version = '222'
    fluent_name = 'save-view'
    _python_name = 'save_view'
    argument_names = ['view_name']
    _child_classes = dict(
        view_name=view_name_1,
    )
    return_type = 'object'

class view_list(StringList, AllowedValuesMixin):
    """
    'view_list' child.
    """
    _version = '222'
    fluent_name = 'view-list'
    _python_name = 'view_list'
    return_type = 'object'

class write_views(Command):
    """
    Write selected views to a view file.
    
    Parameters
    ----------
        file_name : str
            'file_name' child.
        view_list : List
            'view_list' child.
    """
    _version = '222'
    fluent_name = 'write-views'
    _python_name = 'write_views'
    argument_names = ['file_name', 'view_list']
    _child_classes = dict(
        file_name=file_name,
        view_list=view_list,
    )
    return_type = 'object'

class views(Group):
    """
    'views' child.
    """
    _version = '222'
    fluent_name = 'views'
    _python_name = 'views'
    child_names = ['picture_options', 'camera', 'display_states']
    command_names = ['save_picture', 'auto_scale', 'reset_to_default_view', 'delete_view', 'last_view', 'next_view', 'restore_view', 'read_views', 'save_view', 'write_views']
    _child_classes = dict(
        picture_options=picture_options,
        camera=camera,
        display_states=display_states,
        save_picture=save_picture,
        auto_scale=auto_scale_1,
        reset_to_default_view=reset_to_default_view,
        delete_view=delete_view,
        last_view=last_view,
        next_view=next_view,
        restore_view=restore_view,
        read_views=read_views,
        save_view=save_view,
        write_views=write_views,
    )
    return_type = 'object'

class graphics(Group):
    """
    'graphics' child.
    """
    _version = '222'
    fluent_name = 'graphics'
    _python_name = 'graphics'
    child_names = ['mesh', 'contour', 'vector', 'pathlines', 'particle_tracks', 'lic', 'views']
    _child_classes = dict(
        mesh=mesh_1,
        contour=contour,
        vector=vector,
        pathlines=pathlines,
        particle_tracks=particle_tracks,
        lic=lic,
        views=views,
    )
    return_type = 'object'

class methods_2(String, AllowedValuesMixin):
    """
    'methods' child.
    """
    _version = '222'
    fluent_name = 'methods'
    _python_name = 'methods'
    return_type = 'object'

class x(Real):
    """
    'x' child.
    """
    _version = '222'
    fluent_name = 'x'
    _python_name = 'x'
    return_type = 'object'

class y(Real):
    """
    'y' child.
    """
    _version = '222'
    fluent_name = 'y'
    _python_name = 'y'
    return_type = 'object'

class z(Real):
    """
    'z' child.
    """
    _version = '222'
    fluent_name = 'z'
    _python_name = 'z'
    return_type = 'object'

class point_vector(RealList):
    """
    'point_vector' child.
    """
    _version = '222'
    fluent_name = 'point-vector'
    _python_name = 'point_vector'
    return_type = 'object'

class point_normal(RealList):
    """
    'point_normal' child.
    """
    _version = '222'
    fluent_name = 'point-normal'
    _python_name = 'point_normal'
    return_type = 'object'

class compute_from_view_plane(Boolean):
    """
    'compute_from_view_plane' child.
    """
    _version = '222'
    fluent_name = 'compute-from-view-plane?'
    _python_name = 'compute_from_view_plane'
    return_type = 'object'

class surface_aligned_normal(String, AllowedValuesMixin):
    """
    'surface_aligned_normal' child.
    """
    _version = '222'
    fluent_name = 'surface-aligned-normal'
    _python_name = 'surface_aligned_normal'
    return_type = 'object'

class p0_1(RealList):
    """
    'p0' child.
    """
    _version = '222'
    fluent_name = 'p0'
    _python_name = 'p0'
    return_type = 'object'

class p1(RealList):
    """
    'p1' child.
    """
    _version = '222'
    fluent_name = 'p1'
    _python_name = 'p1'
    return_type = 'object'

class p2(RealList):
    """
    'p2' child.
    """
    _version = '222'
    fluent_name = 'p2'
    _python_name = 'p2'
    return_type = 'object'

class bounded(Boolean):
    """
    'bounded' child.
    """
    _version = '222'
    fluent_name = 'bounded?'
    _python_name = 'bounded'
    return_type = 'object'

class sample_point(Boolean):
    """
    'sample_point' child.
    """
    _version = '222'
    fluent_name = 'sample-point?'
    _python_name = 'sample_point'
    return_type = 'object'

class edges_2(IntegerList):
    """
    'edges' child.
    """
    _version = '222'
    fluent_name = 'edges'
    _python_name = 'edges'
    return_type = 'object'

class plane_surface_child(Group):
    """
    'child_object_type' of plane_surface.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'plane_surface_child'
    child_names = ['methods', 'x', 'y', 'z', 'point_vector', 'point_normal', 'compute_from_view_plane', 'surface_aligned_normal', 'p0', 'p1', 'p2', 'bounded', 'sample_point', 'edges']
    _child_classes = dict(
        methods=methods_2,
        x=x,
        y=y,
        z=z,
        point_vector=point_vector,
        point_normal=point_normal,
        compute_from_view_plane=compute_from_view_plane,
        surface_aligned_normal=surface_aligned_normal,
        p0=p0_1,
        p1=p1,
        p2=p2,
        bounded=bounded,
        sample_point=sample_point,
        edges=edges_2,
    )
    return_type = 'object'

class plane_surface(NamedObject[plane_surface_child], CreatableNamedObjectMixinOld[plane_surface_child]):
    """
    'plane_surface' child.
    """
    _version = '222'
    fluent_name = 'plane-surface'
    _python_name = 'plane_surface'
    child_object_type = plane_surface_child
    return_type = 'object'

class surfaces_1(Group):
    """
    'surfaces' child.
    """
    _version = '222'
    fluent_name = 'surfaces'
    _python_name = 'surfaces'
    child_names = ['plane_surface']
    _child_classes = dict(
        plane_surface=plane_surface,
    )
    return_type = 'object'

class results(Group):
    """
    'results' child.
    """
    _version = '222'
    fluent_name = 'results'
    _python_name = 'results'
    child_names = ['graphics', 'surfaces']
    _child_classes = dict(
        graphics=graphics,
        surfaces=surfaces_1,
    )
    return_type = 'object'

class initialize(Command):
    """
    Start Parametric Study.
    
    Parameters
    ----------
        project_filename : str
            'project_filename' child.
    """
    _version = '222'
    fluent_name = 'initialize'
    _python_name = 'initialize'
    argument_names = ['project_filename']
    _child_classes = dict(
        project_filename=project_filename,
    )
    return_type = 'object'

class copy_design_points(Boolean):
    """
    'copy_design_points' child.
    """
    _version = '222'
    fluent_name = 'copy-design-points'
    _python_name = 'copy_design_points'
    return_type = 'object'

class duplicate(Command):
    """
    Duplicate Parametric Study.
    
    Parameters
    ----------
        copy_design_points : bool
            'copy_design_points' child.
    """
    _version = '222'
    fluent_name = 'duplicate'
    _python_name = 'duplicate'
    argument_names = ['copy_design_points']
    _child_classes = dict(
        copy_design_points=copy_design_points,
    )
    return_type = 'object'

class study_name(String):
    """
    'study_name' child.
    """
    _version = '222'
    fluent_name = 'study-name'
    _python_name = 'study_name'
    return_type = 'object'

class set_as_current(Command):
    """
    Set As Current Study.
    
    Parameters
    ----------
        study_name : str
            'study_name' child.
    """
    _version = '222'
    fluent_name = 'set-as-current'
    _python_name = 'set_as_current'
    argument_names = ['study_name']
    _child_classes = dict(
        study_name=study_name,
    )
    return_type = 'object'

class use_base_data(Command):
    """
    Use Base Data.
    """
    _version = '222'
    fluent_name = 'use-base-data'
    _python_name = 'use_base_data'
    return_type = 'object'

class filepath(String):
    """
    'filepath' child.
    """
    _version = '222'
    fluent_name = 'filepath'
    _python_name = 'filepath'
    return_type = 'object'

class export_design_table(Command):
    """
    Export Design Point Table.
    
    Parameters
    ----------
        filepath : str
            'filepath' child.
    """
    _version = '222'
    fluent_name = 'export-design-table'
    _python_name = 'export_design_table'
    argument_names = ['filepath']
    _child_classes = dict(
        filepath=filepath,
    )
    return_type = 'object'

class delete_existing(Boolean):
    """
    'delete_existing' child.
    """
    _version = '222'
    fluent_name = 'delete-existing'
    _python_name = 'delete_existing'
    return_type = 'object'

class import_design_table(Command):
    """
    Import Design Point Table.
    
    Parameters
    ----------
        filepath : str
            'filepath' child.
        delete_existing : bool
            'delete_existing' child.
    """
    _version = '222'
    fluent_name = 'import-design-table'
    _python_name = 'import_design_table'
    argument_names = ['filepath', 'delete_existing']
    _child_classes = dict(
        filepath=filepath,
        delete_existing=delete_existing,
    )
    return_type = 'object'

class write_data(Boolean):
    """
    'write_data' child.
    """
    _version = '222'
    fluent_name = 'write-data'
    _python_name = 'write_data'
    return_type = 'object'

class capture_simulation_report_data(Boolean):
    """
    'capture_simulation_report_data' child.
    """
    _version = '222'
    fluent_name = 'capture-simulation-report-data'
    _python_name = 'capture_simulation_report_data'
    return_type = 'object'

class create_1(CommandWithPositionalArgs):
    """
    Add new Design Point.
    
    Parameters
    ----------
        write_data : bool
            'write_data' child.
        capture_simulation_report_data : bool
            'capture_simulation_report_data' child.
    """
    _version = '222'
    fluent_name = 'create'
    _python_name = 'create'
    argument_names = ['write_data', 'capture_simulation_report_data']
    _child_classes = dict(
        write_data=write_data,
        capture_simulation_report_data=capture_simulation_report_data,
    )
    return_type = 'object'

class design_point(String):
    """
    'design_point' child.
    """
    _version = '222'
    fluent_name = 'design-point'
    _python_name = 'design_point'
    return_type = 'object'

class duplicate_1(Command):
    """
    Duplicate Design Point.
    
    Parameters
    ----------
        design_point : str
            'design_point' child.
    """
    _version = '222'
    fluent_name = 'duplicate'
    _python_name = 'duplicate'
    argument_names = ['design_point']
    _child_classes = dict(
        design_point=design_point,
    )
    return_type = 'object'

class load_case_data(Command):
    """
    Loads relevant case/data file for current design point.
    """
    _version = '222'
    fluent_name = 'load-case-data'
    _python_name = 'load_case_data'
    return_type = 'object'

class design_points_1(StringList):
    """
    'design_points' child.
    """
    _version = '222'
    fluent_name = 'design-points'
    _python_name = 'design_points'
    return_type = 'object'

class delete_design_points(Command):
    """
    Delete Design Points.
    
    Parameters
    ----------
        design_points : List
            'design_points' child.
    """
    _version = '222'
    fluent_name = 'delete-design-points'
    _python_name = 'delete_design_points'
    argument_names = ['design_points']
    _child_classes = dict(
        design_points=design_points_1,
    )
    return_type = 'object'

class separate_journals(Boolean):
    """
    'separate_journals' child.
    """
    _version = '222'
    fluent_name = 'separate-journals'
    _python_name = 'separate_journals'
    return_type = 'object'

class save_journals(Command):
    """
    Save Journals.
    
    Parameters
    ----------
        separate_journals : bool
            'separate_journals' child.
    """
    _version = '222'
    fluent_name = 'save-journals'
    _python_name = 'save_journals'
    argument_names = ['separate_journals']
    _child_classes = dict(
        separate_journals=separate_journals,
    )
    return_type = 'object'

class clear_generated_data(Command):
    """
    Clear Generated Data.
    
    Parameters
    ----------
        design_points : List
            'design_points' child.
    """
    _version = '222'
    fluent_name = 'clear-generated-data'
    _python_name = 'clear_generated_data'
    argument_names = ['design_points']
    _child_classes = dict(
        design_points=design_points_1,
    )
    return_type = 'object'

class update_current(Command):
    """
    Update Current Design Point.
    """
    _version = '222'
    fluent_name = 'update-current'
    _python_name = 'update_current'
    return_type = 'object'

class update_all(Command):
    """
    Update All Design Point.
    """
    _version = '222'
    fluent_name = 'update-all'
    _python_name = 'update_all'
    return_type = 'object'

class update_selected(Command):
    """
    Update Selected Design Points.
    
    Parameters
    ----------
        design_points : List
            'design_points' child.
    """
    _version = '222'
    fluent_name = 'update-selected'
    _python_name = 'update_selected'
    argument_names = ['design_points']
    _child_classes = dict(
        design_points=design_points_1,
    )
    return_type = 'object'

class input_parameters(Map):
    """
    Input Parameter Values of Design Point.
    """
    _version = '222'
    fluent_name = 'input-parameters'
    _python_name = 'input_parameters'
    return_type = 'object'

class output_parameters(Map):
    """
    Output Parameter Values of Design Point.
    """
    _version = '222'
    fluent_name = 'output-parameters'
    _python_name = 'output_parameters'
    return_type = 'object'

class write_data_1(Boolean):
    """
    WriteData option for Design Point.
    """
    _version = '222'
    fluent_name = 'write-data'
    _python_name = 'write_data'
    return_type = 'object'

class capture_simulation_report_data_1(Boolean):
    """
    Capture Simulation Report Data option for Design Point.
    """
    _version = '222'
    fluent_name = 'capture-simulation-report-data'
    _python_name = 'capture_simulation_report_data'
    return_type = 'object'

class design_points_child(Group):
    """
    'child_object_type' of design_points.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'design_points_child'
    child_names = ['input_parameters', 'output_parameters', 'write_data', 'capture_simulation_report_data']
    _child_classes = dict(
        input_parameters=input_parameters,
        output_parameters=output_parameters,
        write_data=write_data_1,
        capture_simulation_report_data=capture_simulation_report_data_1,
    )
    return_type = 'object'

class design_points(NamedObject[design_points_child], CreatableNamedObjectMixinOld[design_points_child]):
    """
    'design_points' child.
    """
    _version = '222'
    fluent_name = 'design-points'
    _python_name = 'design_points'
    command_names = ['create_1', 'duplicate', 'load_case_data', 'delete_design_points', 'save_journals', 'clear_generated_data', 'update_current', 'update_all', 'update_selected']
    _child_classes = dict(
        create_1=create_1,
        duplicate=duplicate_1,
        load_case_data=load_case_data,
        delete_design_points=delete_design_points,
        save_journals=save_journals,
        clear_generated_data=clear_generated_data,
        update_current=update_current,
        update_all=update_all,
        update_selected=update_selected,
    )
    child_object_type = design_points_child
    return_type = 'object'

class current_design_point(String):
    """
    Name of Current Design Point.
    """
    _version = '222'
    fluent_name = 'current-design-point'
    _python_name = 'current_design_point'
    return_type = 'object'

class parametric_studies_child(Group):
    """
    'child_object_type' of parametric_studies.
    """
    _version = '222'
    fluent_name = 'child-object-type'
    _python_name = 'parametric_studies_child'
    child_names = ['design_points', 'current_design_point']
    _child_classes = dict(
        design_points=design_points,
        current_design_point=current_design_point,
    )
    return_type = 'object'

class parametric_studies(NamedObject[parametric_studies_child], CreatableNamedObjectMixinOld[parametric_studies_child]):
    """
    'parametric_studies' child.
    """
    _version = '222'
    fluent_name = 'parametric-studies'
    _python_name = 'parametric_studies'
    command_names = ['initialize', 'duplicate', 'set_as_current', 'use_base_data', 'export_design_table', 'import_design_table']
    _child_classes = dict(
        initialize=initialize,
        duplicate=duplicate,
        set_as_current=set_as_current,
        use_base_data=use_base_data,
        export_design_table=export_design_table,
        import_design_table=import_design_table,
    )
    child_object_type = parametric_studies_child
    return_type = 'object'

class current_parametric_study(String):
    """
    Name of Current Parametric Study.
    """
    _version = '222'
    fluent_name = 'current-parametric-study'
    _python_name = 'current_parametric_study'
    return_type = 'object'

class root(Group):
    """
    'root' object.
    """
    _version = '222'
    fluent_name = ''
    _python_name = 'root'
    child_names = ['file', 'setup', 'solution', 'results', 'parametric_studies', 'current_parametric_study']
    _child_classes = dict(
        file=file,
        setup=setup,
        solution=solution,
        results=results,
        parametric_studies=parametric_studies,
        current_parametric_study=current_parametric_study,
    )
    return_type = 'object'

