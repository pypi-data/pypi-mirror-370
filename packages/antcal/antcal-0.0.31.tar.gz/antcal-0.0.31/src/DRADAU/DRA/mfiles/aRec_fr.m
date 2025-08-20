%--------------------------------------------------------------------------
%                                aRec_fr.m                                   
%--------------------------------------------------------------------------
%  Analyse d'un r�sonateur rectangulaire (fran�ais)                                              
%
%    A) ENTR�ES
%
%    1. 'w' = Largeur du r�sonateur (en cm)
%    2. 'd' = Profondeur du r�sonateur (en cm)
%    3. 'h' = Hauteur du r�sonateur (en cm)
%    4. 'er' = Constante di�lectrique du r�sonateur
%    5. 'VSWR' = taux d'ondes stationnaires tol�r� pour le calcul    
%       de la bande passante d'imp�dance
%
%    B) SORTIES
%
%    - Fr�quence de r�sonance, facteur Q et bande passante d'imp�dance
%      pour les modes : TE(x)d11, TE(y)1d1 et TE(z)11d. Le mode TE(z)11d
%      est pour un r�sonateur isol� (sans plan de masse).
%--------------------------------------------------------------------------
%  R�f�rence :
%
%  - R.K. Mongia et A. Ittipiboon, "Theoretical and experimental
%    investigations on rectangular dielectric resonator antennas", IEEE
%    Transactions on antennas and propagation, Vol. 45, Num. 9, septembre
%    1997, pp. 1348-1356.
%--------------------------------------------------------------------------
%  Note : Ce fichier fait partie de l'Outil de conception et d'analyse 
%         des r�sonateurs di�lectriques (DRA.m).
%
%  Programmation : Alexandre Perron (perrona@emt.inrs.ca)               
%  Affiliation : Institut national de la recherche scientifique (INRS)  
%  Derni�re modification : Le 31 juillet 2008                              
%--------------------------------------------------------------------------

function aRec_fr

% Ent�te :
clc
disp(strvcat('===============================================================',...
             ' Outil de conception et d''analyse des r�sonateur di�lectriques',...
             '==============================================================='));
disp(sprintf('\n----------- Analyse d''un r�sonateur rectangulaire -------------'));

w = [];
while isempty(w)||(isnumeric(w) == 0),
    w = input('\nEntrez la largeur (w) du r�sonateur (en cm) : ');
end

d = [];
while isempty(d)||(isnumeric(d) == 0),
    d = input('\nEntrez la profondeur (d) du r�sonateur (en cm) : ');
end

h = [];
while isempty(h)||(isnumeric(h) == 0),
    h = input('\nEntrez la hauteur (h) du r�sonateur (en cm) : ');
end

er = [];
while isempty(er)||(isnumeric(er) == 0),
    er = input('\nEntrez la constante di�lectrique (er) du r�sonateur : ');
end
    
VSWR = [];
while isempty(VSWR)||(isnumeric(VSWR) == 0),
    VSWR = input('\nEntrez le VSWR pour le calcul de la bande passante (ex.: 2) : ');
end
        

%===============================%
% Calculs pour le mode TE(x)d11 %
%===============================%

% Fr�quence de r�sonance (en GHz) :
syms x
ky = pi/w;
kz = pi/2/h;
k0 = sqrt((x^2+ky^2+kz^2)/er);
f = vectorize(real(x*tan(x*d/2)-sqrt((er-1)*k0^2-x^2)));
kx = fzero(inline(f),[0 pi/d-0.001]);
freq_TEx = 299792458/2/pi*sqrt((kx^2+ky^2+kz^2)/er)/1e7;
% Facteur-Q
We = 8.854e-12*er*w*2*h*d/32*(1+sin(kx*d)/kx/d)*(ky^2+kz^2);
pm = -i*2*pi*freq_TEx*1e7*8*8.854e-12*(er-1)/kx/ky/kz*sin(kx*d/2);
k0 = sqrt((kx^2+ky^2+kz^2)/er);
Prad = 10*k0^4*norm(pm)^2;
facteurQ_TEx = 4*pi*freq_TEx*1e7*We/Prad; 
% Bande passante :
BW_TEx = (VSWR-1)/(sqrt(VSWR)*facteurQ_TEx)*100;

%===============================%
% Calculs pour le mode TE(y)1d1 %
%===============================%

% Fr�quence de r�sonance (en GHz) :
syms y
kx = pi/d; 
kz = pi/2/h;
k0 = sqrt((kx^2+y^2+kz^2)/er);
f = vectorize(real(y*tan(y*w/2)-sqrt((er-1)*k0^2-y^2)));
ky = fzero(inline(f),[0 pi/w-0.001]);
freq_TEy = 299792458/2/pi*sqrt((kx^2+ky^2+kz^2)/er)/1e7;
% Facteur-Q
We = 8.854e-12*er*w*2*h*d/32*(1+sin(ky*w)/ky/w)*(kx^2+kz^2);
pm = -i*2*pi*freq_TEy*1e7*8*8.854e-12*(er-1)/kx/ky/kz*sin(ky*w/2);
k0 = sqrt((kx^2+ky^2+kz^2)/er);
Prad = 10*k0^4*norm(pm)^2;
facteurQ_TEy = 4*pi*freq_TEy*1e7*We/Prad; 
% Bande passante :
BW_TEy = (VSWR-1)/(sqrt(VSWR)*facteurQ_TEy)*100;

%===============================%
% Calculs pour le mode TE(z)11d %
%===============================%

% Fr�quence de r�sonance (en GHz) :
syms z
kx = pi/d;
ky = pi/w;
k0 = sqrt((kx^2+ky^2+z^2)/er);
f = vectorize(z*tan(z*h)-sqrt((er-1)*k0^2-z^2));
kz = fzero(inline(f),[0 pi/2/h-0.001]);
freq_TEz = 299792458/2/pi*sqrt((kx^2+ky^2+kz^2)/er)/1e7;
% Facteur-Q
We = 8.854e-12*er*w*2*h*d/32*(1+sin(kz*2*h)/kz/2/h)*(kx^2+ky^2);
pm = -i*2*pi*freq_TEz*1e7*8*8.854e-12*(er-1)/kx/ky/kz*sin(kz*h);
k0 = sqrt((kx^2+ky^2+kz^2)/er);
Prad = 10*k0^4*norm(pm)^2;
facteurQ_TEz = 4*pi*freq_TEz*1e7*We/Prad; 
% Bande passante :
BW_TEz = (VSWR-1)/(sqrt(VSWR)*facteurQ_TEz)*100;

% Ent�te :
clc
disp(strvcat('===============================================================',...
             ' Outil de conception et d''analyse des r�sonateur di�lectriques',...
             '==============================================================='));
disp(sprintf('\n----------- Analyse d''un r�sonateur rectangulaire -------------\n'));

% Affichage des param�tres d'entr�e :
disp(sprintf('Largeur (w) du r�sonateur (en cm) = %5.4f',w));
disp(sprintf('Profondeur (d) du r�sonateur (en cm) = %5.4f',d));
disp(sprintf('Hauteur (h) du r�sonateur (en cm) = %5.4f',h));
disp(sprintf('Constante di�lectrique du r�sonateur = %5.4f',er));

% Affichage des r�sultats
disp(sprintf('\n'));
disp(strvcat('                  Mode TE(x)d11                  ', ...
             '-------------------------------------------------'));
disp(sprintf('    Fr�quence de r�sonance (en GHz) = %5.4f',freq_TEx));
disp(sprintf('                          Facteur-Q = %5.4f',facteurQ_TEx));
disp(sprintf('    Bande passante (en pourcentage) = %5.4f',BW_TEx));

disp(sprintf('\n'));
disp(strvcat('                  Mode TE(y)1d1                  ', ...
             '-------------------------------------------------'));
disp(sprintf('    Fr�quence de r�sonance (en GHz) = %5.4f',freq_TEy));
disp(sprintf('                          Facteur-Q = %5.4f',facteurQ_TEy));
disp(sprintf('    Bande passante (en pourcentage) = %5.4f',BW_TEy));

disp(sprintf('\n'));
disp(strvcat('     Mode TE(z)11d (pour un r�sonateur isol�)    ', ...
             '-------------------------------------------------'));
disp(sprintf('    Fr�quence de r�sonance (en GHz) = %5.4f',freq_TEz));
disp(sprintf('                          Facteur-Q = %5.4f',facteurQ_TEz));
disp(sprintf('    Bande passante (en pourcentage) = %5.4f',BW_TEz));

end