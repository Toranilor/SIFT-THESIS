function result = dehomogenise(strain,deltaT,MME,nMatrixIP,nFibreIP,nArrays,nAngles)
%SIFT_user(strain,deltaT,MME,nMatrixIP,nFibreIP,nArrays,nAngles,crit,results
%dehomogenise Summary of this function goes here
%   Detailed explanation goes here
    inputStrain = tensor(strain);
    for iAngle = 1:nAngles
        theta = (iAngle-1)/nAngles * 0.5*pi;
        xAxis = [1.,0.,0.];
        yAxis = [0.,cos(theta),sin(theta)];
        rotStrain(:,iAngle) = inputStrain.strainTransform(xAxis,yAxis);
    end
    
    modStrain = zeros(6,max(nMatrixIP,nFibreIP),nArrays,nAngles);
    for iPosition = 1:nMatrixIP
        for iArray = 1:nArrays
            for iAngle = 1:nAngles
                modStrain(:,iPosition,iArray,iAngle) = MME(:,1:6,iPosition,iArray)*rotStrain(:,iAngle);
                modStrain(:,iPosition,iArray,iAngle) = modStrain(:,iPosition,iArray,iAngle)+deltaT*MME(:,7,iPosition,iArray);
                matrixDil(iPosition,iArray,iAngle) = sift.eDil(modStrain(:,iPosition, iArray, iAngle));
                matrixDis(iPosition,iArray,iAngle) = sift.eDis(modStrain(:,iPosition, iArray, iAngle));
            end
        end
    end
    
  %  modStrain(:) = 0.;
  %  for iPosition = 1:nFibreIP
  %      for iArray = 1:nArrays
  %          for iAngle = 1:nAngles
  %              modStrain(:,iPosition,iArray,iAngle) = MME(:,1:6,iPosition+nMatrixIP,iArray)*rotStrain(:,iAngle);
  %              modStrain(:,iPosition,iArray,iAngle) = modStrain(:,iPosition,iArray,iAngle)+deltaT*MME(:,7,iPosition+nMatrixIP,iArray);
  %              fibreDis(iPosition,iArray,iAngle) = sift.eDis(modStrain(:,iPosition, iArray, iAngle));
  %          end
  %      end
  %  end
    
    %Find maximum invariants and assign them to output
    %%Create containers for results
    result = sift.result;
    invariant = sift.invariant;
    location = sift.location;
    
    %Find maximum invariants and store the index in column format
    [invariant.matrixDil , matrixDilLocInd] = max( matrixDil(:) );
    [invariant.matrixDis , matrixDisLocInd] = max( matrixDis(:) );
    %[invariant.fibreDis , fibreDisLocInd] = max( fibreDis(:) );
    
    %Store the critical location in a location index
    [point,array,angle] = ind2sub([max(nMatrixIP,nFibreIP),nArrays,nAngles],matrixDilLocInd);
    location.matrixDil = sift.locationIndex([point,array,angle]);
    [point,array,angle] = ind2sub([max(nMatrixIP,nFibreIP),nArrays,nAngles],matrixDisLocInd);
    location.matrixDis = sift.locationIndex([point,array,angle]);
    %[point,array,angle] = ind2sub([max(nMatrixIP,nFibreIP),nArrays,nAngles],fibreDisLocInd);
    %location.fibreDis = sift.locationIndex([point,array,angle]);
    %Construct result
    result.invariant = invariant;
    result.location = location;
end

