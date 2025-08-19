!> Wrapper for interfacing `m_get_wavelength` with python
!>
!> Written by hand here.
!> Generation to be automated in future (including docstrings of some sort).
!> One other note:
!> This function returns a standard Fortran type.
!> In future, we will want to add in returning Fortran derived types too.
!> Doing that will require adding in an extra 'manager' layer
!> so there will be one extra file compared to what we have here.
module m_get_wavelength_w  ! Convention to date: just suffix wrappers with _w

    use m_get_wavelength, only: o_get_wavelength => get_wavelength
    ! We won't always need the renaming trick,
    ! but here we do as the wrapper function
    ! and the original function should have the same name.
    ! ("o_" for original)

    implicit none
    private

    public :: get_wavelength

contains

    pure function get_wavelength(frequency) result(wavelength)

        ! Annoying that this has to be injected everywhere,
        ! but ok it can be automated.
        integer, parameter :: dp = selected_real_kind(15, 307)

        real(kind=dp), intent(in) :: frequency
            !! Frequency

        real(kind=dp) :: wavelength
            !! Corresponding wavelength

        wavelength = o_get_wavelength(frequency)

    end function get_wavelength

end module m_get_wavelength_w
