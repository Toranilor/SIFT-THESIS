classdef tensor
    %tensor Summary of this class goes here
    %   Detailed explanation goes here
    
    properties
        xx
        yy
        zz
        xy
        yz
        zx
    end
    
    methods
        function obj=tensor(strain)
            obj.xx = strain(1);
            obj.yy = strain(2);
            obj.zz = strain(3);
            obj.xy = strain(4);
            obj.yz = strain(5);
            obj.zx = strain(6);
        end

        function d = double(obj)
            d = [obj.xx,obj.yy,obj.zz,obj.xy,obj.yz,obj.zx]';
        end
        
        function r = plus(obj1,obj2)
            [a,b] = clean(obj1,obj2);
            r = tensor(a+b);
        end
        
        function r = minus(obj1,obj2);
            [a,b] = clean(obj1,obj2);
            r = tensor(a-b);
        end
                
        function r = uminus(obj)
            a = double(obj);
            r = tensor(-a);
        end
        
        function r = uplus(obj)
            r = obj;
        end
        
        function r = mtimes(obj1,obj2)
            [a,b] = clean(obj1,obj2);
            r = tensor(a*b);
        end
        
        function r = mrdivide(obj1,obj2)
            [a,b] = clean(obj1,obj2);
            r = tensor(a/b);
        end
        
        function [a,b] = clean(obja,objb);
            aClass = class(obja);
            switch aClass
                case 'tensor'
                    a = double(obja);
                otherwise
                    a = obja;
            end
            
            bClass = class(objb);
            switch bClass
                case 'tensor'
                    b = double(objb);
                otherwise
                    b = objb;
            end
            
        end   
        
        function r = transform(obj, xNew, xyNew)
            basis = eye(3);
            
            xPrime = xNew;
            zPrime = cross(xNew,xyNew);
            yPrime = cross(zPrime,xPrime);
            
            xPrime = xPrime / mag(xPrime);
            yPrime = yPrime / mag(yPrime);
            zPrime = zPrime / mag(zPrime);
            
            basisPrime(:,1) = xPrime;
            basisPrime(:,2) = yPrime;
            basisPrime(:,3) = zPrime;
            
            L(:,:) = 0.0d0;
            A(:,:) = 0.0d0;

            for iRow = 1:3
                for iColumn = 1:3
                    L(iRow,iColumn) = dot(basisPrime(:,iRow),basis(:,iColumn));
                end
            end
            
            Lup     = circshift(L, [-1  0]);
            Lleft   = circshift(L, [ 0 -1]);
            Lupleft = circshift(L, [-1 -1]);

            A(1:3,1:3) = L.*L;
            A(1:3,4:6) = 2*L.*Lleft;
            A(4:6,1:3) = L.*Lup;
            A(4:6,4:6) = L.*Lupleft + Lup.*Lleft;
                        
            r = A*obj;
            
            function r = mag(v)
                r = sqrt(dot(v,v));
            end
        end
        
        function r = strainTransform(obj, xNew, xyNew)
            strain = obj;
            strain.xy = strain.xy/2;
            strain.yz = strain.yz/2;
            strain.zx = strain.zx/2;
            
            strain = strain.transform(xNew,xyNew);
            
            strain.xy = strain.xy*2;
            strain.yz = strain.yz*2;
            strain.zx = strain.zx*2;
            
            r = strain;
        end
        
    end
 
end

