%--------------------------------------------------------------------------
%                                dHemi_fr.m                                   
%--------------------------------------------------------------------------
%  Conception d'un r�sonateur h�misph�rique (fran�ais)                                              
%
%    A) ENTR�ES
%
%    1. 'freq' = fr�quence de r�sonance vis�e                        
%    2. 'choix_mode' = mode de rayonnement choisi             
%    3. 'er' = constante di�lectrique du mat�riau disponible (facultatif)
%    4. 'BW' = bande passante fractionnelle minimale (ou exacte) d�sir�e         
%    5. 'VSWR' = taux d'ondes stationnaires tol�r� pour le calcul    
%       de la bande passante d'imp�dance
%
%    B) SORTIES
%
%    - Rayon du r�sonateur, facteur Q, bande passante d'imp�dance et 
%      constante di�lectrique relative (si non sp�cifi�e).
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
%  Derni�re modification : Le 31 juillet 2008                              
%--------------------------------------------------------------------------

function dHemi_fr

% Ent�te :
clc
disp(strvcat('===============================================================',...
             ' Outil de conception et d''analyse des r�sonateur di�lectriques',...
             '==============================================================='));
disp(sprintf('\n--------- Conception d''un r�sonateur h�misph�rique ------------'));

% Entr�e des param�tres
freq = [];
while isempty(freq)||(isnumeric(freq) == 0)
   freq = input('\nEntrez la fr�quence de r�sonance d�sir�e (en GHz) : ');
end

choix_mode = [];
while isempty(choix_mode)||(choix_mode ~= 1 && choix_mode ~= 2)
    choix_mode = input(['\nPour quel mode de rayonnement?\n',...
                        '   (1) Mode TE111 (maximum au flanc)\n', ...
                        '   (2) Mode TM101 (z�ro au flanc)\n', ...
                        'Faites votre choix : ']);
end

er = [];
while isempty(er)||(isnumeric(er) == 0),
   er = input('\nEntrez la constante di�lectrique du r�sonateur\nou ''0'' si vous ne voulez pas la sp�cifier : ');
end

BW = [];
if (er ~= 0)
    while isempty(BW)||(isnumeric(BW) == 0)
        BW = input('\nEntrez la bande passante fractionelle minimale (ex.: 0.05 pour 5%) : ');
    end
else
    while isempty(BW)||(isnumeric(BW) == 0)
        BW = input('\nEntrez la bande passante fractionelle d�sir�e (ex.: 0.05 pour 5%) : ');
    end
end    

VSWR = [];
while isempty(VSWR)||(isnumeric(VSWR) == 0)
    VSWR = input('\nEntrez le VSWR pour le calcul de la bande passante (ex.: 2) : ');
end

repeter = 1;
while (repeter == 1)
    
    % Calcul du facteur Q � partir de la bande passante sp�cifi�e :
    facteurQ_max = (VSWR-1)/(sqrt(VSWR)*BW);
    facteurQ = [];

    % Si la constante di�lectrique est sp�cifi�e par l'utilisateur, il faut
    % v�rifier s'il est possible d'obtenir la bande passante d�sir�e pour le
    % mode de rayonnement choisi :
    if(er ~= 0)
        switch choix_mode
            case 1
                facteurQ = 0.08+0.796*er+0.01226*er^2-3e-5*er^3;
                ka = 2.8316*er^-0.47829;
            case 2
                if (er <= 20)
                    facteurQ = 0.723+0.9324*er-0.0956*er^2+0.00403*er^3-5e-5*er^4;
                else
                    facteurQ = 2.621-0.574*er+0.02812*er^2+2.59e-4*er^3;
                end
                ka = 4.47226*er^-0.505;
        end
        
        % Si ce n'est pas possible, il faut que l'utilisateur change certaines sp�cifications :
        if (facteurQ_max < facteurQ)
            choix = [];
            while isempty(choix)||(choix ~= 1 && choix ~= 2 && choix ~= 3 && choix ~= 4)
                choix = input(['\nLa bande passante minimale ne peut �tre atteinte pour ce mode pour la\n',...
                               'constante di�lectrique choisie. D�sirez-vous :\n', ...
                               '   (1) Modifier la constante di�lectrique du r�sonateur?\n', ...
                               '   (2) Modifier la bande passante minimale?\n', ...
                               '   (3) Choisir un autre mode de rayonnement?\n', ...
                               '   (4) Retourner au menu principal?\n', ...
                               'Faites votre choix : ']);
            end
            
            switch choix
                case 1
                    er = [];
                    while isempty(er)||(isnumeric(er) == 0)
                        er = input('\nEntrez la nouvelle constante di�lectrique du r�sonateur\nou ''0'' si vous ne voulez pas la sp�cifier : ');
                    end
                case 2
                    BW = [];
                    while isempty(BW)||(isnumeric(BW) == 0)
                        BW = input('\nEntrez la nouvelle bande passante fractionnelle minimale (ex.: 0.05 pour 5%) : ');
                    end
                case 3
                    choix_mode = [];
                    while isempty(choix_mode)||(choix_mode ~= 1 && choix_mode ~= 2)
                        choix_mode = input(['\nPour quel mode de rayonnement?\n',...
                                            '   (1) Mode TE111 (maximum au flanc)\n', ...
                                            '   (2) Mode TM101 (z�ro au flanc)\n', ...
                                            'Faites votre choix : ']);
                    end
                case 4    
                    return
            end

        
        else
            repeter = 0;
        end    

    else
        switch choix_mode
        case 1
            er_calc = fsolve(@(x)0.08+0.796*x+0.01226*x^2-3e-5*x^3-facteurQ_max,50);
            ka = 2.8316*er_calc^-0.47829;
        case 2
            if (facteurQ_max <= 5.371)
                er_calc = fsolve(@(x)0.723+0.9324*x-0.0956*x^2+0.00403*x^3-5e-5*x^4-facteurQ_max,10);
            else
                er_calc = fsolve(@(x)2.621-0.574*x+0.02812*x^2+2.59e-4*x^3-facteurQ_max,60);
            end
            ka = 4.47226*er_calc^-0.505;
        end

        % Un message d'erreur est affich� si le constante di�lectrique
        % calcul�e est plus petite que 1 :
        if (er_calc < 1)
            choix = [];
            while isempty(choix)||(choix ~= 1 && choix ~= 2 && choix ~= 3 && choix ~= 4)
                choix = input(['\nLa bande passante d�sir�e ne peut �tre atteinte pour ce mode car la constante\n',...
                               'di�lectrique requise est physiquement irr�alisable (er < 1). D�sirez-vous :\n', ...
                               '   (1) Sp�cifier une constante di�lectrique?\n', ...
                               '   (2) Modifier la bande passante d�sir�e?\n', ...
                               '   (3) Choisir un autre mode de rayonnement?\n', ...
                               '   (4) Retourner au menu principal?\n', ...
                               'Faites votre choix : ']);
            end
            
            switch choix
                case 1
                    er = [];
                    while isempty(er)||(isnumeric(er) == 0)
                        er = input('\nEntrez la constante di�lectrique du r�sonateur : ');
                    end
                case 2
                    BW = [];
                    while isempty(BW)||(isnumeric(BW) == 0)
                        BW = input('\nEntrez la nouvelle bande passante fractionnelle d�sir�e (ex.: 0.05 pour 5%) : ');
                    end
                case 3
                    choix_mode = [];
                    while isempty(choix_mode)||(choix_mode ~= 1 && choix_mode ~= 2)
                        choix_mode = input(['\nPour quel mode de rayonnement?\n',...
                                            '   (1) Mode TE111 (maximum au flanc)\n', ...
                                            '   (2) Mode TM101 (z�ro au flanc)\n', ...
                                            'Faites votre choix : ']);
                    end
                case 4    
                    return
            end
        else
            repeter = 0;
        end    
    end
    
    if (repeter == 0)
        
        % Lorsque tous les param�tres sont corrects, le rayon du r�sonateur est calcul� :
        a = 4.7713*ka/freq;
        
        % Calcul de la bande passante obtenue (si une constante di�lectrique est sp�cifi�e) :
        if (er ~= 0)
            BW_reelle = (VSWR-1)/(sqrt(VSWR)*facteurQ)*100;
        end    
          
        % Ent�te :
        clc
        disp(strvcat('===============================================================',...
                     ' Outil de conception et d''analyse des r�sonateur di�lectriques',...
                     '==============================================================='));
        disp(sprintf('\n--------- Conception d''un r�sonateur h�misph�rique ------------\n'));

        % Affichage des param�tres d'entr�e :
        disp(sprintf('Fr�quence de r�sonance d�sir�e (en GHz) = %5.4f',freq));
    
        if (choix_mode == 1)
            disp(sprintf('Mode de rayonnement = TE111'));
        else
            disp(sprintf('Mode de rayonnement = TM101'));
        end

        if (er ~= 0)
            disp(sprintf('Bande passante fractionnelle minimale = %5.4f',BW));
        else
            disp(sprintf('Bande passante fractionnelle d�sir�e = %5.4f',BW));
        end
        
        disp(sprintf('VSWR pour le calcul de la bande passante = %5.4f',VSWR));
        
        if (er ~= 0)
            disp(sprintf('Constante di�lectrique du r�sonateur = %5.4f',er));
        end
        
        % Affichage des r�sultats :
        disp(sprintf('\n'));
        disp(strvcat('       R�sultats pour le mode choisi        ', ...
                     '--------------------------------------------'));
        disp(sprintf('     Rayon (a) du r�sonateur (en cm) = %5.4f',a));
        if (er == 0)
            disp(sprintf('Constante di�lectrique du r�sonateur = %5.4f',er_calc));
            disp(sprintf('                           Facteur-Q = %5.4f',facteurQ_max));
        else
            disp(sprintf('                           Facteur-Q = %5.4f',facteurQ));
            disp(sprintf('     Bande passante (en pourcentage) = %5.4f',BW_reelle));
        end
    end
end

end