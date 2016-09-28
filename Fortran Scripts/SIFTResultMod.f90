module SIFTResultMod
implicit none
private
public :: tSIFTResult, nullSIFTResult
public :: tSIFTInvariant, nullInvariant
public :: assignment(=)

type :: tSIFTInvariant
	real(kind=8) :: matrixDil
    real(kind=8) :: matrixDis
    real(kind=8) :: fibreDil
    real(kind=8) :: fibreDis
endtype
type(tSIFTInvariant), parameter :: nullInvariant = tSIFTInvariant(0.0d0,0.0d0,0.0d0,0.0d0)

type :: tSIFTLocationIndex
	integer :: point
	integer :: array
	integer :: angle
endtype
type(tSIFTLocationIndex), parameter :: nullLocIndex = tSIFTLocationIndex(0,0,0)

type :: tSIFTLocation
	type(tSIFTLocationIndex) :: matrixDil
    type(tSIFTLocationIndex) :: matrixDis
    type(tSIFTLocationIndex) :: fibreDil
    type(tSIFTLocationIndex) :: fibreDis
endtype
type(tSIFTLocation), parameter :: nullLocation = tSIFTLocation(nullLocIndex,nullLocIndex,nullLocIndex,nullLocIndex)

type :: tSIFTResult
	type(tSIFTInvariant) :: invariant
	type(tSIFTInvariant) :: index
	type(tSIFTLocation) :: location
endtype
type(tSIFTResult), parameter :: nullSIFTResult = tSIFTResult(nullInvariant,nullInvariant,nullLocation)

interface assignment (=)
	module procedure arrayToIndex
	module procedure indexToArray
end interface

contains
	pure subroutine arrayToIndex(index, array)
	type(tSIFTLocationIndex), intent(out) :: index
	real(kind=8), dimension(3), intent(in) :: array
	index%point = array(1)
	index%array = array(2)
	index%angle = array(3)
	end subroutine arrayToIndex
	
	pure subroutine indexToArray(array, index)
	real(kind=8), dimension(6), intent(out) :: array
	type(tSIFTLocationIndex), intent(in) :: index
	array(1) = index%point
	array(2) = index%array
	array(3) = index%angle
	end subroutine indexToArray
end module