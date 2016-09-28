module SIFTMod
	use,intrinsic :: ISO_FORTRAN_ENV
	use TensorMod
	use SIFTResultMod
	implicit none
	private
	public :: eDil, eDis, SIFT    ! Public functions
	public :: tSIFTResult, tSIFTInvariant, nullSIFTResult, nullInvariant ! Public data types
	!public :: critInvariant ! Public parameters
	interface SIFT
		module procedure SIFT_default
		module procedure SIFT_user
	end interface SIFT
	integer, parameter :: nMicroComponents = 6, nMacroComponents = 7
	integer, parameter :: nMatrixIP = 4, nFibreIP = 3
	integer, parameter :: nArrays = 2, nAngles = 12
	real(kind=8), dimension(nMicroComponents, nMacroComponents, (nMatrixIP+nFibreIP), nArrays) :: SAF

	! USER PARAMETERS

	type(tSIFTInvariant), parameter :: critInvariant = tSIFTInvariant(0.033,0.118,1e12,1e12)

   ! Strain Amplification Values
   include 'MME_T300_Cycom970_0.60.inc' ! Be clever here about formatting this string (maybe put the fibre selection and everything INSIDE the include

contains

   pure function eDil(Strain)
      real(kind=8) :: eDil
      type(tTensor), intent(in) :: strain
      eDil = strain%xx + strain%yy + strain%zz
   end function eDil

   pure function eDis(Strain)
      real(kind=8) :: eDis
      type(tTensor), intent(in) :: strain
      real(kind=8) :: j1Val, crossTerms, shearTerms
      real(kind=8), dimension(6) :: strainVector

      strainVector = strain
      j1Val = strain%xx + strain%yy + strain%zz
      crossTerms = dot_product(strainVector(1:3), cshift(strainVector(1:3),1))
      shearTerms = dot_product(strainVector(4:6), strainVector(4:6))
      eDis = j1Val * j1Val
      eDis = eDis + 0.75d0 * shearTerms
      eDis = eDis - 3.0d0 * crossTerms
      eDis = eDis / 3.0d0
      eDis = sqrt(eDis)
   end function eDis

   subroutine SIFT_user(strain,deltaT,MME,nMatrixIP,nFibreIP,nArrays,nAngles,crit,results)
      type(tTensor), intent(in) :: strain
      real(kind=8), intent(in) :: deltaT
      real(kind=8), dimension(nMicroComponents,nMacroComponents,(nMatrixIP+nFibreIP),nArrays), intent(in) :: MME
      integer, intent(in) :: nMatrixIP,nFibreIP,nArrays,nAngles
      type(tSIFTInvariant), intent(in) :: crit
      type(tSIFTResult), intent(out) :: results

      integer :: iPosition, iArray, iAngle, iMacro, iMicro
      type(tTensor), dimension(nAngles) :: rotStrain
      real(kind=8), dimension(nMatrixIP, nArrays, nAngles) :: matrixDil, matrixDis
      real(kind=8), dimension(nFibreIP, nArrays, nAngles) :: fibreDil, fibreDis
      type(tTensor), dimension(max(nMatrixIP,nFibreIP), nArrays, nAngles) :: modStrain
      real(kind=8) :: rotAngle
      real(kind=8), dimension(3) :: tempLocation

      do iAngle = 1,nAngles
         rotAngle = (iAngle-1)*acos(-1.0d0)/nAngles
         rotStrain(iAngle) = tensorRotAboutX(strain,rotAngle)
      enddo

      !   Matrix Calculations. SAF stored in SAF(1:nMatrixIP).
      modStrain(:,:,:) = TensorZero
      forall (iPosition = 1:nMatrixIP, iArray = 1:nArrays, iAngle = 1:nAngles)
         modStrain(iPosition,iArray,iAngle) = MME(:,1:6,iPosition,iArray)*rotStrain(iAngle)
         modStrain(iPosition,iArray,iAngle) = modStrain(iPosition,iArray,iAngle)+deltaT*MME(:,7,iPosition,iArray)
         matrixDil(iPosition,iArray,iAngle) = eDil(modStrain(iPosition, iArray, iAngle))
         matrixDis(iPosition,iArray,iAngle) = eDis(modStrain(iPosition, iArray, iAngle))
      end forall

      !   Fibre Calculations. SAF stored in SAF(nMatrixIP+1:nMatrixIP+nFibreIP)
      modStrain(:,:,:) = TensorZero
      forall (iPosition = 1:nFibreIP, iArray = 1:nArrays, iAngle = 1:nAngles)
         modStrain(iPosition,iArray,iAngle) = MME(:,1:6,iPosition+nMatrixIP, iArray) * rotStrain(iAngle)
         modStrain(iPosition,iArray,iAngle) = modStrain(iPosition, iArray, iAngle)+deltaT*MME(:,7,iPosition+nMatrixIP,iArray)
         fibreDis(iPosition,iArray,iAngle) = eDis(modStrain(iPosition,iArray,iAngle))
      end forall

      results = nullSIFTResult
      results%invariant%matrixDil = maxval(matrixDil)
      results%invariant%matrixDis = maxval(matrixDis)
      results%invariant%fibreDil = 0.0d0
      results%invariant%fibreDis = maxval(fibreDis)

      results%index%matrixDil = results%invariant%matrixDil / crit%matrixDil
      results%index%matrixDis = results%invariant%matrixDis / crit%matrixDis
      results%index%fibreDil = results%invariant%fibreDil / crit%fibreDil
      results%index%fibreDis = results%invariant%fibreDis / crit%fibreDis

      tempLocation = maxloc(matrixDil)
      results%location%matrixDil = tempLocation
      tempLocation = maxloc(matrixDis)
      results%location%matrixDis = tempLocation
      tempLocation = 0
      results%location%fibreDil = tempLocation
      tempLocation = maxloc(fibreDis)
      results%location%fibreDis = tempLocation
   end subroutine SIFT_user

   subroutine SIFT_default(strain,deltaT,results)
      type(tTensor), intent(in) :: strain
      real(kind=8), intent(in) :: deltaT
      type(tSIFTResult), intent(out) :: results

      integer :: iPosition, iArray, iAngle, iMacro, iMicro
      type(tTensor), dimension(nAngles) :: rotStrain
      real(kind=8), dimension(nMatrixIP, nArrays, nAngles) :: matrixDil, matrixDis
      real(kind=8), dimension(nFibreIP, nArrays, nAngles) :: fibreDil, fibreDis
      type(tTensor), dimension(max(nMatrixIP,nFibreIP), nArrays, nAngles) :: modStrain
      real(kind=8) :: rotAngle
      real(kind=8), dimension(3) :: tempLocation

      do iAngle = 1,nAngles
         rotAngle = (iAngle-1)*acos(-1.0d0)/nAngles
         rotStrain(iAngle) = tensorRotAboutX(strain,rotAngle)
      enddo

      !   Matrix Calculations. SAF stored in SAF(1:nMatrixIP).
      modStrain(:,:,:) = TensorZero
      forall (iPosition = 1:nMatrixIP, iArray = 1:nArrays, iAngle = 1:nAngles)
         modStrain(iPosition,iArray,iAngle) = SAF(:,1:6,iPosition,iArray)*rotStrain(iAngle)
         modStrain(iPosition,iArray,iAngle) = modStrain(iPosition,iArray,iAngle)+deltaT*SAF(:,7,iPosition,iArray)
         matrixDil(iPosition,iArray,iAngle) = eDil(modStrain(iPosition, iArray, iAngle))
         matrixDis(iPosition,iArray,iAngle) = eDis(modStrain(iPosition, iArray, iAngle))
      end forall

      !   Fibre Calculations. SAF stored in SAF(nMatrixIP+1:nMatrixIP+nFibreIP)
      modStrain(:,:,:) = TensorZero
      forall (iPosition = 1:nFibreIP, iArray = 1:nArrays, iAngle = 1:nAngles)
         modStrain(iPosition,iArray,iAngle) = SAF(:,1:6,iPosition+nMatrixIP, iArray) * rotStrain(iAngle)
         modStrain(iPosition,iArray,iAngle) = modStrain(iPosition, iArray, iAngle)+deltaT*SAF(:,7,iPosition+nMatrixIP,iArray)
         fibreDis(iPosition,iArray,iAngle) = eDis(modStrain(iPosition,iArray,iAngle))
      end forall

      results = nullSIFTResult
      results%invariant%matrixDil = maxval(matrixDil)
      results%invariant%matrixDis = maxval(matrixDis)
      results%invariant%fibreDil = 0.0d0
      results%invariant%fibreDis = maxval(fibreDis)

      results%index%matrixDil = results%invariant%matrixDil / critInvariant%matrixDil
      results%index%matrixDis = results%invariant%matrixDis / critInvariant%matrixDis
      results%index%fibreDil = results%invariant%fibreDil / critInvariant%fibreDil
      results%index%fibreDis = results%invariant%fibreDis / critInvariant%fibreDis

      tempLocation = maxloc(matrixDil)
      results%location%matrixDil = tempLocation
      tempLocation = maxloc(matrixDis)
      results%location%matrixDis = tempLocation
      tempLocation = 0
      results%location%fibreDil = tempLocation
      tempLocation = maxloc(fibreDis)
      results%location%fibreDis = tempLocation
   end subroutine SIFT_default
end module SIFTMod
