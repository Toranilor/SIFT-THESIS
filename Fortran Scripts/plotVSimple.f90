subroutine plotv(v,s,sp,etot,eplas,ecreep,t,n,nn,kc,ndi,nshear,jpltcd)
! * * * * *
!
!     define a variable for contour plotting (user subroutine).
!
!     v		variable to be put onto the post file
!     s (idss)     stress array
!     sp	     stresses in preferred direction
!     etot	   total strain (generalized)
!     eplas	  total plastic strain
!     ecreep	 total creep strain
!     t		array of state variable (temperature first)
!     m(1)	   user element number
!     m(2)	   internal element number
!     m(3)	   material id
!     m(4)	   internal material id
!     nn	     integration point number
!     kc(1)	layer number
!     kc(2)	internal layer number
!     ndi	    number of direct stress components
!     nshear	 number of shear stress components
!     jpltcd	 the absolute value of the user's entered post code
!
!
!	  the components of s, sp, etot, eplas and ecreep are given in the order
!	  as defined in volume B for the current element.
!
! * * * * *
use,intrinsic :: iso_fortran_env
use SIFTMod
use TensorMod
use simData
implicit none

integer :: jpltcd, ndi, nn, nshear
integer, dimension(4), intent(in) :: n
integer, dimension(2), intent(in) :: kc
real(kind=8), dimension(1), intent(in) ::  t
real(kind=8), dimension(6), intent(in) :: ecreep, eplas, etot, s, sp
real(kind=8), intent(out) :: v

v = 5.0d0

end subroutine plotv