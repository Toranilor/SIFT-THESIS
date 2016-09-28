classdef locationIndex
    %SIFTLOCATIONINDEX Summary of this class goes here
    %   Detailed explanation goes here
    
    properties
        point
        array
        angle
    end
    
    methods
        function obj=locationIndex(arrayLocation)
            obj.point=arrayLocation(1);
            obj.array=arrayLocation(2);
            obj.angle=arrayLocation(3);
        end
    end
    
end

