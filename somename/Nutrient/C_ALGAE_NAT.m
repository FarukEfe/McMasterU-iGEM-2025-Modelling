% Estimations of the steady-state algae concentration in natural optimized conditions

% TO-DOs:
% (2) Add yield and revenue model, profit and cost model to maximize for profit

function dydt = ODEsystem(~, y, params)
    % ODEs - Algal Growth by Nutrient Input
    p = 0.4; % q (mu_g/L/day)
    [pi_1, pi_2] = deal(0.6, 0.3);
    [a_0, a_1, a_2] = deal(0.1, 0.05, 0.03);
    [k_1, k_2] = deal(0.1, 0.4);
    [k_11, k_13, k_22, k_23] = deal(1,1,2,1);
    [lambda_1, lambda_2] = deal(0.05, 0.6);
    [b_10, omega, delta] = deal(0.05, 0.8, 0.9);
    % Optimizing Parameters | q = 0.2 and pi_d = 0.1 originally
    q = params(1); pi_d = params(2);

    dydt = zeros(5,1);
    % Algal Growth Based on Nutrients
    dydt(1) = (1-pi_d)*q - a_0*y(1) - (k_1*y(1)*y(3)/(k_13+k_11*y(1))) + (1-p)*omega*delta*y(4); % Nitrogen Concentration in microgram/L
    dydt(2) = pi_d*q - a_1*y(2) - (k_2*y(2)*y(3)/(k_23+k_22*y(2))) + p*omega*delta*y(4); % Phosphorus Concentration in microgram/L
    dydt(3) = (lambda_1*k_1*y(1)*y(3)/(k_13+k_11*y(1))) + (lambda_2*k_2*y(2)*y(3)/(k_23+k_22*y(2))) - a_2*y(3) - b_10*(y(3)^2); % Algae Concentration in microgram/L
    dydt(4) = pi_1*a_2*y(3) + pi_2*b_10*(y(3)^2) - delta*y(4); % Detritious Concentration in microgram/L
end

function objective = computeObjective(params, tspan, y0)
    % Solve the ODE with current parameters
    [~, Y] = ode15s(@(t,y) ODEsystem(t, y, params), tspan, y0);
    
    % Define your objective - example: maximize final value of y3
    objective = -Y(end, 3); % Negative because we'll minimize
    % objective = -max(Y(:,3)); % Maximum of y3
    % objective = -(Y(end,3) - Y(1,3)); % Change in y3
    % objective = -trapz(tspan, Y(:,3)); % Area under y3 curve
end

% Optimization setup
tspan = [0 200]; % Extended time for system to stabilize
y0 = [0.1; 0.1; 0.1; 0.1; 0.1]; % Initial conditions

% Parameter bounds [q, p, lambda_1, lambda_2]
lb = [1, 0]; % Lower bounds
ub = [100, 1]; % Upper bounds

% Initial guess (middle of bounds)
params0 = [0.2, 0.1];

% Optimization options
options = optimoptions('fmincon', 'Display', 'iter', 'Algorithm', 'sqp');

% Run optimization
[optimalParams, maxValue] = fmincon(@(p) computeObjective(p, tspan, y0), ...
                                   params0, [], [], [], [], lb, ub, [], options);

% Display results
fprintf('Optimal parameters:\n');
fprintf('input N = %.4f\n', optimalParams(1));
fprintf('input P = %.4f\n', optimalParams(2));
fprintf('Maximum y3 value achieved: %.4f\n', -maxValue);

% Visualize optimal solution
[time, Y_optimal] = ode45(@(t,y) ODEsystem(t, y, optimalParams), tspan, y0);

figure;
subplot(2,1,1);
plot(time, Y_optimal(:,1:2));
legend('N(t)', 'P(t)');
title('Optimal Solution - N(t) and P(t)');

subplot(2,1,2);
plot(time, Y_optimal(:,3:4));
legend('A(t)', 'D(t)');
title('Optimal Solution - A(t) and D(t)');

subplot()