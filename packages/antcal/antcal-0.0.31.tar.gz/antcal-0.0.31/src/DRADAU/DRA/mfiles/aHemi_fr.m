%--------------------------------------------------------------------------
%                                aHemi_fr.m                                   
%--------------------------------------------------------------------------
%  Analyse d'un r�sonateur h�misph�rique (fran�ais)                                              
%
%    A) ENTR�ES
%    
%    1. 'a' = rayon du r�sonateur (en cm)
%    2. 'er' = constante di�lectrique relative du r�sonateur
%    3. 'VSWR' = taux d'ondes stationnaires tol�r� pour le calcul    
%       de la bande passante d'imp�dance
%
%    B) SORTIES
%    
%    - Fr�quence de r�sonance, facteur Q et bande passante d'imp�dance
%      pour les deux premiers modes : TE111 et TM101.
%--------------------------------------------------------------------------
%  R�f�rence :
%
%  - M. Gastine, L. Courtois et J.J. Dormann, "Electromagnetic resonances
%    of free dielectric spheres", IEEE Transactions on microwave theory
%    and techniques, Vol. 15, Num. 12, d�cembre 1967, pp. 694-700.
%--------------------------------------------------------------------------
%  Note : Ce fichier fait partie de l'Outil de conception et d'analyse 
%         des r�sonateurs di�lectriques (DRA.m). Les �quations d'estimation
%         sont tir�es du livre "Dielectric resonator antenna handbook" de
%         Also Petosa.
%
%  Programmation : Alexandre Perron (perrona@emt.inrs.ca)               
%  Affiliation : Institut national de la recherche scientifique (INRS)  
%  Derni�re modification : Le 22 juillet 2008                              
%--------------------------------------------------------------------------

function aHemi_fr

% Ent�te :
clc
disp(strvcat('===============================================================',...
             ' Outil de conception et d''analyse des r�sonateur di�lectriques',...
             '==============================================================='));
disp(sprintf('\n----------- Analyse d''un r�sonateur h�misph�rique -------------'));

% Entr�e des param�tres :
a = [];
while isempty(a)||(isnumeric(a) == 0),
   a = input('\nEntrez le rayon (a) du r�sonateur (en cm) : ');
end

er = [];
while isempty(er)||(isnumeric(er) == 0),
   er = input('\nEntrez la constante di�lectrique (er) du r�sonateur : ');
end

VSWR = [];
while isempty(VSWR)||(isnumeric(VSWR) == 0),
   VSWR = input('\nEntrez le VSWR pour le calcul de la bande passante (ex.: 2) : ');
end

%============================%
% Calculs pour le mode TE111 %
%============================%

% Fr�quence de r�sonance (en GHz) :
freq_TE = 2.8316*er^-0.47829*4.7713/a;
% Facteur Q :
facteurQ_TE = 0.08+0.796*er+0.01226*er^2-3e-5*er^3;
% Bande passante :
BW_TE = (VSWR-1)/(sqrt(VSWR)*facteurQ_TE)*100;

%============================%
% Calculs pour le mode TM101 %
%============================%

% Fr�quence de r�sonance (en GHz) :
freq_TM = 4.47226*er^-0.505*4.7713/a;
% Facteur Q :
if (er <= 20)
    facteurQ_TM = 0.723+0.9324*er-0.0956*er^2+0.00403*er^3-5e-5*er^4;
else
    facteurQ_TM = 2.621-0.574*er+0.02812*er^2+2.59e-4*er^3;
end
% Bande passante :
BW_TM = (VSWR-1)/(sqrt(VSWR)*facteurQ_TM)*100;

% Ent�te :
clc
disp(strvcat('===============================================================',...
             ' Outil de conception et d''analyse des r�sonateur di�lectriques',...
             '==============================================================='));
disp(sprintf('\n----------- Analyse d''un r�sonateur h�misph�rique -------------\n'));

% Affichage des param�tres d'entr�e :
disp(sprintf('Rayon (a) du r�sonateur (en cm) = %5.4f',a));
disp(sprintf('Constante di�lectrique du r�sonateur = %5.4f',er));
disp(sprintf('VSWR pour le calcul de la bande passante = %5.4f',VSWR));

% Affichage des r�sultats :
disp(sprintf('\n'));
disp(strvcat('                   Mode TE111                    ', ...
             '-------------------------------------------------'));
disp(sprintf('    Fr�quence de r�sonance (en GHz) = %5.4f',freq_TE));
disp(sprintf('                          Facteur-Q = %5.4f',facteurQ_TE));
disp(sprintf('    Bande passante (en pourcentage) = %5.4f',BW_TE));

disp(sprintf('\n'));
disp(strvcat('                   Mode TM101                    ', ...
             '-------------------------------------------------'));
disp(sprintf('    Fr�quence de r�sonance (en GHz) = %5.4f',freq_TM));
disp(sprintf('                          Facteur-Q = %5.4f',facteurQ_TM));
disp(sprintf('    Bande passante (en pourcentage) = %5.4f',BW_TM));

end