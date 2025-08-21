!     !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!     PyXMAKE - %pyx_module%
!     %pyx_module% library
!     !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

!     ======================================================================================						          	          
!     Description:
!>    @brief
!>    Create a module of %pyx_module% to avoid namespace pollution
!>    @details
!>    This module simply wraps %pyx_module% and leaves the original source code as is. 
!>    @author 
!>    Marc Garbade
!>    @date
!>    12.07.2019
!>    @par Notes/Changes
!>    - Created 												// mg 12.07.2019
!     ======================================================================================	  
!DEC$ IF DEFINED(PYX_WRAPPER)
      MODULE %pyx_module%
      CONTAINS
!DEC$ END IF
!	  
#include %pyx_source%
!
!DEC$ IF DEFINED(PYX_WRAPPER)	  
      END MODULE %pyx_module%
!DEC$ END IF