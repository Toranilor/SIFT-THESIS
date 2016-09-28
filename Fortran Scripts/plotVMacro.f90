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

type(tSIFTResult) :: elemInvariant = nullSIFTResult !Setting this to zero here ensures that is automatically saves the value for recurring calls
real(kind=8) :: deltaTemp, rotAng !should get temperatures directly from marc.

character(len=24) :: materialName
integer(int8) :: materialType = 0

type(tTensor) :: strainElastic, strainElasPref
!type(tSIFTResult) :: SIFTResult

select case (jpltcd)
case (1)	!	Maximum Diliational Strain Invariant
	call matName(n(3:4),materialName)
	materialType = matPlot(materialName) ! 0 = No Plot, 1 = Homogenous, 2 = Composite
	if (materialType == 0) then
		v = 0.0d0
	else
		strainElastic = getStrainElastic()
		if (materialType == 1) then
			v = eDil(strainElastic)
		else
			!
			!   Calculate strain in preferred CS
			!
			strainElasPref = prefOrientation(strainElastic) ! Rotation to new coordinates 
			deltaTemp = cureTemp - simTemp
			!
			!   Call SIFT subroutine. Only needs to be called once because the results will save for the next subroutine call.
			!
			call SIFT(strainElasPref,deltaTemp,SAF,nMatrixIP,nFibreIP,nArrays,nAngles,critInvariant,elemInvariant)
			v = elemInvariant%invariant%matrixDil
		endif
	endif
case (2)	!	Maximum Distortional Strain Invariant
	if (materialType == 0) then
		v = 0.0d0
	elseif (materialType == 1) then
		v = eDis(strainElastic)
	else
		v = elemInvariant%invariant%matrixDis
	endif
case (3)	!	Maximum Distortional Strain Invariant Fibre
	if (materialType == 0) then
		v = 0.0d0
	elseif (materialType == 1) then
		v = 0.0d0
	else
		v = elemInvariant%invariant%fibreDis
	endif
case (4)	!	Dilitational Strain Invariant Index
	if (materialType == 0) then
		v = 0.0d0
	elseif (materialType == 1) then
		v = eDil(strainElastic) / critInvariant%matrixDil
	else
		v = elemInvariant%index%matrixDil
	endif
case (5)	!	Distortional Strain Invariant Index
	if (materialType == 0) then
		v = 0.0d0
	elseif (materialType == 1) then
		v = eDis(strainElastic) / critInvariant%matrixDis
	else
		v = elemInvariant%index%matrixDis
	endif
case (6)	!	Distortional Strain Invariant Index Fibre
	if (materialType == 0) then
		v = 0.0d0
	elseif (materialType == 1) then
		v = 0.0d0
	else
		v = elemInvariant%index%fibreDis
	endif
case (7)	!   Maximum Amplified Strain Invariant Index
	if (materialType == 0) then
		v = 0.0d0
	elseif (materialType == 1) then
		v = 0.0d0
	else
		v = max(elemInvariant%index%matrixDil,elemInvariant%index%matrixDis)
	endif
case (8)	!   Maximum Dilitational Location: Point
	v = elemInvariant%location%matrixDil%point
case (9)	!   Maximum Dilitational Location: Array
	v = elemInvariant%location%matrixDil%array
case (10)	!   Maximum Dilitational Location: angle
	v = elemInvariant%location%matrixDil%angle
case (11)	!   Maximum Distortional Location: Point
	v = elemInvariant%location%matrixDis%point
case (12)	!   Maximum Distortional Location: Array
	v = elemInvariant%location%matrixDis%array
case (13)	!   Maximum Distortional Location: angle
	v = elemInvariant%location%matrixDis%angle
case (20)	!   Damage index matrix
	v = dIndexCurr(n(1),nn,2)
case (21)	!   Damage index fibre
	v = dIndexCurr(n(1),nn,1)
case default
	v = 0.0d0
end select
return
contains
	function getStrainElastic()
		type(tTensor) :: getStrainElastic
		real(kind=8), dimension(6) :: strainArray
		type(tTensor) :: strainTotal, strainThermal
		strainArray = 0.0d0
		!call elmvar(301,n(1),nn,kc(1),strainArray) ! Total strain tensor from initial condition
		!strainTotal = strainArray
		!call elmvar(371,n(1),nn,kc(1),strainArray) ! Thermal strain tensor from initial condition
		!strainThermal = strainArray
		call elmvar(401,n(1),nn,kc(1),strainArray) ! Elastic strain tensor from mechanical model
		getStrainElastic = strainArray
		!getStrainElastic = getStrainElastic + strainTotal - strainThermal ! New elastic strain tensor accounting for residual strains
	end function
	function prefOrientation(strain)
		implicit none
		type(ttensor) :: prefOrientation
		type(ttensor), intent(in) :: strain
		real(real64), dimension(3) :: xOrient,yOrient
		call elmvar(691,n(1),nn,kc(1),xOrient) ! orientation vector of element coordinate system
		call elmvar(694,n(1),nn,kc(1),yOrient) ! orientation vector of element coordinate 
		prefOrientation = strainCoordTransfer(strain,xOrient,yOrient)
	end function
end subroutine plotv