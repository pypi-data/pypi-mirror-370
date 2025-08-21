"""Load Schemas"""
from pydantic import Field, root_validator, constr
from typing import Union
from enum import Enum

from ._base import IDdEnergyBaseModel
from .schedule import ScheduleRuleset, ScheduleFixedInterval
from ..altnumber import Autocalculate


class PeopleAbridged(IDdEnergyBaseModel):

    type: constr(regex='^PeopleAbridged$') = 'PeopleAbridged'

    people_per_area: float = Field(
        ...,
        ge=0,
        description='People per floor area expressed as [people/m2]'
    )

    occupancy_schedule: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description='Identifier of a schedule for the occupancy over the course of the '
        'year. The type of this schedule should be Fractional and the fractional '
        'values will get multiplied by the people_per_area to yield a complete '
        'occupancy profile.'
    )

    activity_schedule: str = Field(
        default=None,
        min_length=1,
        max_length=100,
        description='Identifier of a schedule for the activity of the occupants over '
        'the course of the year. The type of this schedule should be ActivityLevel '
        'and the values of the schedule equal to the number of Watts given off by an '
        'individual person in the room. If None, a default constant schedule with '
        '120 Watts per person will be used, which is typical of awake, adult humans '
        'who are seated.'
    )

    radiant_fraction: float = Field(
        0.3,
        ge=0,
        le=1,
        description='The radiant fraction of sensible heat released by people. '
        '(Default: 0.3).'
    )

    latent_fraction: Union[Autocalculate, float] = Field(
        Autocalculate(),
        ge=0,
        le=1,
        description='Number for the latent fraction of heat gain due to people or '
        'an Autocalculate object.'
    )

    @root_validator
    def check_sum_fractions(cls, values):
        "Ensure sum is less than 1."
        rad = values.get('radiant_fraction')
        latent = values.get('latent_fraction')
        if latent is not None and isinstance(latent, float):
            assert rad + latent <= 1, \
                'Sum of radiant and latent fractions cannot be greater than 1.'
        return values


class People(PeopleAbridged):

    type: constr(regex='^People$') = 'People'

    occupancy_schedule: Union[ScheduleRuleset, ScheduleFixedInterval] = Field(
        ...,
        description='A schedule for the occupancy over the course of the '
        'year. The type of this schedule should be Fractional and the fractional '
        'values will get multiplied by the people_per_area to yield a complete '
        'occupancy profile.'
    )

    activity_schedule: Union[ScheduleRuleset, ScheduleFixedInterval] = Field(
        default=None,
        description='A schedule for the activity of the occupants over the '
        'course of the year. The type of this schedule should be ActivityLevel '
        'and the values of the schedule equal to the number of Watts given off by an '
        'individual person in the room. If None, a default constant schedule with '
        '120 Watts per person will be used, which is typical of awake, adult humans '
        'who are seated.'
    )


class LightingAbridged(IDdEnergyBaseModel):

    type: constr(regex='^LightingAbridged$') = 'LightingAbridged'

    watts_per_area: float = Field(
        ...,
        ge=0,
        description='Lighting per floor area as [W/m2].'
    )

    schedule: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description='Identifier of the schedule for the use of lights over the course '
        'of the year. The type of this schedule should be Fractional and the '
        'fractional values will get multiplied by the watts_per_area to yield a '
        'complete lighting profile.'
    )

    visible_fraction: float = Field(
        0.25,
        ge=0,
        le=1,
        description='The fraction of heat from lights that goes into the zone as '
        'visible (short-wave) radiation. (Default: 0.25).'
    )

    radiant_fraction: float = Field(
        0.32,
        ge=0,
        le=1,
        description='The fraction of heat from lights that is long-wave radiation. '
        '(Default: 0.32).'
    )

    return_air_fraction: float = Field(
        0.0,
        ge=0,
        le=1,
        description='The fraction of the heat from lights that goes into the zone '
        'return air. (Default: 0).'
    )

    baseline_watts_per_area: float = Field(
        11.84029,
        ge=0,
        description='The baseline lighting power density in [W/m2] of floor area. '
        'This baseline is useful to track how much better the installed lights are '
        'in comparison to a standard like ASHRAE 90.1. If set to None, it will '
        'default to 11.84029 W/m2, which is that ASHRAE 90.1-2004 baseline for '
        'an office.'
    )

    @root_validator
    def check_sum_fractions(cls, values):
        "Ensure sum is less than 1."
        return_air = values.get('return_air_fraction')
        vis = values.get('visible_fraction')
        rad = values.get('radiant_fraction')
        assert sum((return_air, vis, rad)) <= 1, \
            'Sum of visible, radiant, and return air fractions cannot be greater than 1.'
        return values


class Lighting(LightingAbridged):

    type: constr(regex='^Lighting$') = 'Lighting'

    schedule: Union[ScheduleRuleset, ScheduleFixedInterval] = Field(
        ...,
        description='The schedule for the use of lights over the course of '
        'the year. The type of this schedule should be Fractional and the '
        'fractional values will get multiplied by the watts_per_area to yield a '
        'complete lighting profile.'
    )


class _EquipmentBase(IDdEnergyBaseModel):

    watts_per_area: float = Field(
        ...,
        ge=0,
        description='Equipment level per floor area as [W/m2].'
    )

    schedule: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description='Identifier of the schedule for the use of equipment over the '
        'course of the year. The type of this schedule should be Fractional and the '
        'fractional values will get multiplied by the watts_per_area to yield '
        'a complete equipment profile.'
    )

    radiant_fraction: float = Field(
        0,
        ge=0,
        le=1,
        description='Number for the amount of long-wave radiation heat given off'
        ' by equipment. Default value is 0.'
    )

    latent_fraction: float = Field(
        0,
        ge=0,
        le=1,
        description='Number for the amount of latent heat given off by '
        'equipment. Default value is 0.'

    )

    lost_fraction: float = Field(
        0,
        ge=0,
        le=1,
        description='Number for the amount of “lost” heat being given off by '
        'equipment. The default value is 0.'
    )

    @root_validator
    def check_sum_fractions(cls, values):
        "Ensure sum is less than 1."
        rad = values.get('radiant_fraction')
        latent = values.get('latent_fraction')
        lost = values.get('lost_fraction')
        assert sum((rad, latent, lost)) <= 1, \
            'Sum of radiant, latent, and lost fractions cannot be greater than 1.'
        return values


class ElectricEquipmentAbridged(_EquipmentBase):

    type: constr(regex='^ElectricEquipmentAbridged$') = 'ElectricEquipmentAbridged'


class ElectricEquipment(ElectricEquipmentAbridged):

    type: constr(regex='^ElectricEquipment$') = 'ElectricEquipment'

    schedule: Union[ScheduleRuleset, ScheduleFixedInterval] = Field(
        ...,
        description='The schedule for the use of equipment over the course '
        'of the year. The type of this schedule should be Fractional and the '
        'fractional values will get multiplied by the watts_per_area to yield '
        'a complete equipment profile.'
    )


class GasEquipmentAbridged(_EquipmentBase):

    type: constr(regex='^GasEquipmentAbridged$') = 'GasEquipmentAbridged'


class GasEquipment(GasEquipmentAbridged):

    type: constr(regex='^GasEquipment$') = 'GasEquipment'

    schedule: Union[ScheduleRuleset, ScheduleFixedInterval] = Field(
        ...,
        description='The schedule for the use of equipment over the course '
        'of the year. The type of this schedule should be Fractional and the '
        'fractional values will get multiplied by the watts_per_area to yield '
        'a complete equipment profile.'
    )


class ServiceHotWaterAbridged(IDdEnergyBaseModel):

    type: constr(regex='^ServiceHotWaterAbridged$') = 'ServiceHotWaterAbridged'

    flow_per_area: float = Field(
        ...,
        ge=0,
        description='Number for the total volume flow rate of water per unit area '
        'of floor [L/h-m2].'
    )

    schedule: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description='Identifier of the schedule for the hot water use over the course '
        'of the year. The type of this schedule should be Fractional and the '
        'fractional values will get multiplied by the flow_per_area to yield a '
        'complete water usage profile.'
    )

    target_temperature: float = Field(
        60,
        gt=0,
        description='Number for the target temperature of water out of the tap (C). '
        'This the temperature after hot water has been mixed with cold water '
        'from the water mains. The default is 60C, which essentially assumes that the '
        'flow_per_area on this object is only for water straight out of the '
        'water heater.'
    )

    sensible_fraction: float = Field(
        0.2,
        ge=0,
        le=1,
        description='A number between 0 and 1 for the fraction of the total hot water '
        'load given off as sensible heat in the zone.'
    )

    latent_fraction: float = Field(
        0.05,
        ge=0,
        le=1,
        description='A number between 0 and 1 for the fraction of the total hot '
        'water load that is latent.'
    )

    @root_validator
    def check_sum_fractions(cls, values):
        "Ensure sum is less than 1."
        sens = values.get('sensible_fraction')
        lat = values.get('latent_fraction')
        assert sum((sens, lat)) <= 1, \
            'Sum of sensible and latent fractions cannot be greater than 1.'
        return values


class ServiceHotWater(ServiceHotWaterAbridged):

    type: constr(regex='^ServiceHotWater$') = 'ServiceHotWater'

    schedule: Union[ScheduleRuleset, ScheduleFixedInterval] = Field(
        ...,
        description='The schedule for the use of hot water over the course of '
        'the year. The type of this schedule should be Fractional and the '
        'fractional values will get multiplied by the flow_per_area to yield a '
        'complete water usage profile.'
    )


class InfiltrationAbridged(IDdEnergyBaseModel):

    type: constr(regex='^InfiltrationAbridged$') = 'InfiltrationAbridged'

    flow_per_exterior_area: float = Field(
        ...,
        ge=0,
        description='Number for the infiltration per exterior surface area in m3/s-m2.'
    )

    schedule: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description='Identifier of the schedule for the infiltration over the course of '
        'the year. The type of this schedule should be Fractional and the '
        'fractional values will get multiplied by the flow_per_exterior_area '
        'to yield a complete infiltration profile.'
    )

    constant_coefficient: float = Field(
        1,
        ge=0
    )

    temperature_coefficient: float = Field(
        0,
        ge=0
    )

    velocity_coefficient: float = Field(
        0,
        ge=0
    )


class Infiltration(InfiltrationAbridged):

    type: constr(regex='^Infiltration$') = 'Infiltration'

    schedule: Union[ScheduleRuleset, ScheduleFixedInterval] = Field(
        ...,
        description='The schedule for the infiltration over the course of '
        'the year. The type of this schedule should be Fractional and the '
        'fractional values will get multiplied by the flow_per_exterior_area '
        'to yield a complete infiltration profile.'
    )


class VentilationAbridged(IDdEnergyBaseModel):

    type: constr(regex='^VentilationAbridged$') = 'VentilationAbridged'

    flow_per_person: float = Field(
        0,
        ge=0,
        description='Intensity of ventilation in[] m3/s per person]. Note that '
        'setting this value does not mean that ventilation is varied based on '
        'real-time occupancy but rather that the design level of ventilation '
        'is determined using this value and the People object of the Room.'
    )

    flow_per_area: float = Field(
        0,
        ge=0,
        description='Intensity of ventilation in [m3/s per m2 of floor area].'
    )

    air_changes_per_hour: float = Field(
        0,
        ge=0,
        description='Intensity of ventilation in air changes per hour (ACH) for '
        'the entire Room.'
    )

    flow_per_zone: float = Field(
        0,
        ge=0,
        description='Intensity of ventilation in m3/s for the entire Room.'
    )

    schedule: str = Field(
        default=None,
        min_length=1,
        max_length=100,
        description='Identifier of the schedule for the ventilation over the course of '
        'the year. The type of this schedule should be Fractional and the '
        'fractional values will get multiplied by the total design flow rate '
        '(determined from the sum of the other 4 fields) to yield a complete '
        'ventilation profile.'
    )


class Ventilation(VentilationAbridged):

    type: constr(regex='^Ventilation$') = 'Ventilation'

    schedule: Union[ScheduleRuleset, ScheduleFixedInterval] = Field(
        default=None,
        description='Schedule for the ventilation over the course of '
        'the year. The type of this schedule should be Fractional and the '
        'fractional values will get multiplied by the total design flow rate '
        '(determined from the sum of the other 4 fields) to yield a complete '
        'ventilation profile.'
    )


class SetpointAbridged(IDdEnergyBaseModel):
    """Used to specify information about the setpoint schedule."""

    type: constr(regex='^SetpointAbridged$') = 'SetpointAbridged'

    cooling_schedule: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description='Identifier of the schedule for the cooling setpoint. The values in '
        'this schedule should be temperature in [C].'
    )

    heating_schedule: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description='Identifier of the schedule for the heating setpoint. The values in '
        'this schedule should be temperature in [C].'
    )

    humidifying_schedule: str = Field(
        default=None,
        min_length=1,
        max_length=100,
        description='Identifier of the schedule for the humidification setpoint. '
        'The values in this schedule should be in [%].'
    )

    dehumidifying_schedule: str = Field(
        default=None,
        min_length=1,
        max_length=100,
        description='Identifier of the schedule for the dehumidification setpoint. '
        'The values in this schedule should be in [%].'
    )

    setpoint_cutout_difference: float = Field(
        0,
        ge=0,
        description='An optional positive number for the temperature '
        'difference between the cutout temperature and the setpoint temperature. '
        'Specifying a non-zero number here is useful for modeling the throttling '
        'range associated with a given setup of setpoint controls and HVAC equipment. '
        'Throttling ranges describe the range where a zone is slightly over-cooled '
        'or over-heated beyond the thermostat setpoint. They are used to avoid '
        'situations where HVAC systems turn on only to turn off a few minutes later, '
        'thereby wearing out the parts of mechanical systems faster. They can '
        'have a minor impact on energy consumption and can often have significant '
        'impacts on occupant thermal comfort, though using the default value '
        'of zero will often yield results that are close enough when trying '
        'to estimate the annual heating/cooling energy use. Specifying a value '
        'of zero effectively assumes that the system will turn on whenever '
        'conditions are outside the setpoint range and will cut out as soon '
        'as the setpoint is reached.'
    )

    @root_validator
    def check_both_humid_sch(cls, values):
        "Ensure that the other humidity schedule is included when one is."
        humid = values.get('humidifying_schedule')
        dehumid = values.get('dehumidifying_schedule')
        if humid is not None:
            assert dehumid is not None, 'When humidifying_schedule is specified, ' \
                'dehumidifying_schedule must also be specified.'
        if dehumid is not None:
            assert humid is not None, 'When dehumidifying_schedule is specified, ' \
                'humidifying_schedule must also be specified.'
        return values


class Setpoint(SetpointAbridged):
    """Used to specify information about the setpoint schedule."""

    type: constr(regex='^Setpoint$') = 'Setpoint'

    cooling_schedule: Union[ScheduleRuleset, ScheduleFixedInterval] = Field(
        ...,
        description='Schedule for the cooling setpoint. The values in '
        'this schedule should be temperature in [C].'
    )

    heating_schedule: Union[ScheduleRuleset, ScheduleFixedInterval] = Field(
        ...,
        description='Schedule for the heating setpoint. The values in '
        'this schedule should be temperature in [C].'
    )

    humidifying_schedule: Union[ScheduleRuleset, ScheduleFixedInterval] = Field(
        default=None,
        description='Schedule for the humidification setpoint. The values '
        'in this schedule should be in [%].'
    )

    dehumidifying_schedule: Union[ScheduleRuleset, ScheduleFixedInterval] = Field(
        default=None,
        description='Schedule for the dehumidification setpoint. The values '
        'in this schedule should be in [%].'
    )


class FuelTypes (str, Enum):
    """Designates the acceptable fuel types for process loads."""
    electricity = 'Electricity'
    natural_gas = 'NaturalGas'
    propane = 'Propane'
    fuel_oil_no_1 = 'FuelOilNo1'
    fuel_oil_no_2 = 'FuelOilNo2'
    diesel = 'Diesel'
    gasoline = 'Gasoline'
    coal = 'Coal'
    steam = 'Steam'
    district_heating = 'DistrictHeating'
    district_cooling = 'DistrictCooling'
    other_fuel_1 = 'OtherFuel1'
    other_fuel_2 = 'OtherFuel2'
    none = 'None'


class ProcessAbridged(IDdEnergyBaseModel):

    type: constr(regex='^ProcessAbridged$') = 'ProcessAbridged'

    watts: float = Field(
        ...,
        ge=0,
        description='A number for the process load power in Watts.'
    )

    schedule: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description='Identifier of the schedule for the use of the process over the '
        'course of the year. The type of this schedule should be Fractional and the '
        'fractional values will get multiplied by the watts to yield a complete '
        'equipment profile.'
    )

    fuel_type: FuelTypes = Field(
        ...,
        description='Text to denote the type of fuel consumed by the process. '
        'Using the "None" type indicates that no end uses will be associated '
        'with the process, only the zone gains.'
    )

    end_use_category: str = Field(
        'Process',
        min_length=1,
        max_length=100,
        description='Text to indicate the end-use subcategory, which will identify '
        'the process load in the end use output. For example, “Cooking”, '
        '“Clothes Drying”, etc. A new meter for reporting is created for each '
        'unique subcategory.'
    )

    radiant_fraction: float = Field(
        0,
        ge=0,
        le=1,
        description='Number for the amount of long-wave radiation heat given off'
        ' by the process load. Default value is 0.'
    )

    latent_fraction: float = Field(
        0,
        ge=0,
        le=1,
        description='Number for the amount of latent heat given off by the process '
        'load. Default value is 0.'

    )

    lost_fraction: float = Field(
        0,
        ge=0,
        le=1,
        description='Number for the amount of “lost” heat being given off by '
        'the process load. The default value is 0.'
    )

    @root_validator
    def check_sum_fractions(cls, values):
        "Ensure sum is less than 1."
        rad = values.get('radiant_fraction')
        latent = values.get('latent_fraction')
        lost = values.get('lost_fraction')
        assert sum((rad, latent, lost)) <= 1, \
            'Sum of radiant, latent, and lost fractions cannot be greater than 1.'
        return values
