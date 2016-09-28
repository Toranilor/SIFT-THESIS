function eDilOut = eDil(strain)
% Calculates a scalar J1 from a vectorised strain tensor
    eDilOut = strain(1) + strain(2) + strain(3);
end

