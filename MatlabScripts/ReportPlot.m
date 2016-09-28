%%Report Printer
CritDis = 0.133;
CritDil = 0.025;
plot(Report(:,8),matrixDil./CritDil,'o',Report(:,8),matrixDis./CritDis,'o');
legend('Dilatational Invariant','Distortional Invariant'); 
hline(0);
title(strcat('Dilatational Vs Distortional Invariant, ',foldername))
xlabel(['Distance in ', subscript(j), ' direction ,mm']);
ylabel('Invariant / Critical Imvariant');
grid on