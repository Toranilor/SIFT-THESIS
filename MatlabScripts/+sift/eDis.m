function eDisOut = eDis(strain)
%EDIS Summary of this function goes here
%   Detailed explanation goes here
    
    d = strain(1:3);
    d_shift = circshift(d,[1 0]);
    shear = strain(4:6);
    J1 = sift.eDil(strain);
    J2 = dot(d,d_shift) - 0.25*dot(shear,shear);
    eDisOut = sqrt(J1*J1/3. - J2);
end

