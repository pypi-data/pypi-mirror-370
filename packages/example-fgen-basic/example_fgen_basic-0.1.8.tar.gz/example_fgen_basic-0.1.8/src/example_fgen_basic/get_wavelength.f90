!> Get wavelength of light
!>
!> `!>` is for documentation that appears before the thing you're documenting
!> (https://forddocs.readthedocs.io/en/stable/user_guide/project_file_options.html#predocmark).
!> `!!` is for documentation that appears after the thing you're documenting
module m_get_wavelength

    use kind_parameters, only: dp

    implicit none
    private

    real(kind=dp), parameter, public :: speed_of_light = 2.99792e8_dp
    !! Speed of light [m/s]

    public :: get_wavelength

contains

    pure function get_wavelength(frequency) result(wavelength)
        !! Get wavelength of light for a given frequency
        !
        ! Trying with FORD style docstrings for now
        ! see https://forddocs.readthedocs.io/en/stable/

        real(kind=dp), intent(in) :: frequency
        !! Frequency

        real(kind=dp) :: wavelength
        !! Corresponding wavelength

        wavelength = speed_of_light / frequency

    end function get_wavelength

end module m_get_wavelength
