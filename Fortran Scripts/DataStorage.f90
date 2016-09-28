module simData
	use,intrinsic :: iso_fortran_env
	use :: SIFTResultMod
	implicit none
	private
	public :: dIndexInc,dIndexCurr
	public :: matPlot, matFail
	public :: degradationFactor, damageIndex
	
	real(real64), dimension(:,:,:), allocatable :: dIndexInc,dIndexCurr
	real(real64), parameter :: fibreSoftening = 0.2d0, matrixSoftening = 0.5d0
	
	! USER PARAMETERS
	public :: fibreType,matrixType,Vf,cureTemp,simTemp,fibreCritDil,fibreCritDis,matrixCritDil,matrixCritDis
	character(len=20), parameter ::		fibreType = 'T300'
	character(len=20), parameter ::		matrixType = 'Cycom970'
	real(real64), parameter ::			Vf = 0.6
	real(real64), parameter ::			cureTemp = 165.d0
	real(real64), parameter ::			simTemp=25.d0
	real(real64), parameter ::			matrixCritDil = 0.033
	real(real64), parameter ::			matrixCritDis = 0.118
	real(real64), parameter ::			fibreCritDil = 1e12
	real(real64), parameter ::			fibreCritDis = 0.025
	public :: nMatrixIP, nFibreIP, nArrays, nAngles
	integer, parameter :: nMatrixIP = 4, nFibreIP = 3
	integer, parameter :: nArrays = 2, nAngles = 12
	
	type(tSIFTInvariant), parameter, public :: critInvariant = tSIFTInvariant(matrixCritDil,matrixCritDis,fibreCritDil,fibreCritDis)
	real(real64), dimension(6, 7, (nMatrixIP+nFibreIP), nArrays),public :: SAF
	include 'MME_T300_Cycom970_0.60.inc'
	
contains
	integer(int8) function matPlot(matName)
		character(len=24) :: matName
		select case (trim(matName))
		case('T300-CYCOM970','Composite','T300-CYCOM970_fail')
			matPlot = 2
		case('FM300')
			matPlot = 1
		case default
			matPlot = 1
		end select
	end function
	
	logical function matFail(matName)
		character(len=24) :: matName
		select case (trim(matName))
		case('T300-CYCOM970','FM300','T300-CYCOM970_fail')
			matFail = .true.
		case('Ti-4V-6Al')
			matFail = .false.
		case default
			matFail = .false.
		end select
	end function
	
	real(real64) function degradationFactor(damageIndex,failureIndex) result(factor)
		real(real64), intent(in) :: damageIndex
		real(real64), intent(in) :: failureIndex
		factor = 1.0d0
		if (damageIndex > 1.0d-6) then
			factor = max((1-damageIndex)**2.0d0,0.05/failureIndex)
		endif
	end function
	
	real(real64) function damageIndex(failureIndex,material) result(index)
		real(real64), intent(in) :: failureIndex
		character, intent(in) :: material
		real(real64) :: soft
		
		select case (material)
		case('f')
			soft = fibreSoftening
		case('m')
			soft = matrixSoftening
		end select
		
		if (failureIndex < 1.0d0) then
			index = 0.0d0
		else if (failureIndex > (1.0d0 + soft)) then
			index = 1.0d0
		else
			index = (failureIndex-1)/soft
		endif
	end function
end module simData