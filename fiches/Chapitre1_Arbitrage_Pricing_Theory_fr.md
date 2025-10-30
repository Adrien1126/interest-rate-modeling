# Chapitre 1 — Introduction à la théorie de la valorisation par absence d'arbitrage

> Brève introduction pédagogique adaptée à l'apprentissage.

---

Ce chapitre présente les outils probabilistes et analytiques minimaux nécessaires à la valorisation moderne sans arbitrage : un espace probabilisé filtré, le mouvement brownien (multidimensionnel), les processus d'Itô élémentaires, le principe d'absence d'arbitrage et les mesures martingales équivalentes. La présentation est concise et vise l'intuition et l'usage pratique.

## 1.1 Notation et cadre

- Nous travaillons sur un espace filtré $(\Omega, \mathcal{F}, (\mathcal{F}_t)_{t\ge0}, \mathbb{P})$ vérifiant les hypothèses usuelles (complétude et filtration droite).
- Les espérances sous $\mathbb{P}$ sont notées $\mathbb{E}^{\mathbb{P}}[\cdot]$ ou simplement $\mathbb{E}[\cdot]$. L'espérance conditionnelle donnée $\mathcal{F}_t$ est $\mathbb{E}[\cdot\,|\,\mathcal{F}_t]$ ou $\mathbb{E}_t[\cdot]$.
- Le temps est continu et non négatif : $t\in[0,\infty)$.

### Mouvement brownien $d$-dimensionnel (processus de Wiener)

Définition (informelle) : un processus $W=(W_t)_{t\ge0}$ à valeurs dans $\mathbb{R}^d$ est un mouvement brownien $d$-dimensionnel sous $\mathbb{P}$ si :

1. $W_0=0$ presque sûrement.
2. Presque sûrement, les trajectoires $t\mapsto W_t(\omega)$ sont continues.
3. Pour $0\le s<t$, l'accroissement $W_t-W_s$ est indépendant de $\mathcal{F}_s$.
4. Pour $0\le s<t$, l'accroissement $W_t-W_s$ suit une loi normale multivariée centrée de covariance $(t-s)I_d$ :

$$
W_t-W_s \sim \mathcal{N}\big(0, (t-s)I_d\big).
$$

Remarques :
- Chaque composante $W^i$ est un mouvement brownien unidimensionnel standard et les composantes sont indépendantes.
- De manière plus générale, on peut considérer une matrice de covariance $(t-s)\Sigma$ avec $\Sigma$ symétrique positive semi-définie ; alors on peut écrire $W_t=\Sigma^{1/2}B_t$ où $B$ est un brownien standard en $\mathbb{R}^d$.

### Processus d'Itô et prix d'actifs

Un mouvement brownien sert à piloter des équations différentielles stochastiques (EDS). Un processus d'Itô vectoriel $X=(X_t)_{t\ge0}$ à valeurs dans $\mathbb{R}^p$ s'écrit :

$$
\mathrm{d}X_t = \mu(t,X_t)\,\mathrm{d}t + \sigma(t,X_t)\,\mathrm{d}W_t,
$$

où $\mu:[0,\infty)\times\mathbb{R}^p\to\mathbb{R}^p$ est le drift et $\sigma:[0,\infty)\times\mathbb{R}^p\to\mathbb{R}^{p\times d}$ la matrice de diffusion. On suppose que $\mu$ et $\sigma$ sont progressivement mesurables et satisfont des conditions de croissance et d'intégrabilité (par exemple Lipschitz) garantissant l'existence et l'unicité des solutions.

En finance, les vecteurs de prix d'actifs (souvent décotés) sont modélisés par des processus d'Itô. Par exemple, pour un actif unique sous la mesure physique $\mathbb{P}$ :

$$
\mathrm{d}S_t = S_t\mu_t\,\mathrm{d}t + S_t\sigma_t\,\mathrm{d}W_t.
$$


> #### Définition 1.1.1 (Martingale)
>
> Soit $Y(t)$ un processus adapté à valeurs vectorielles tel que $\mathbb{E}^{\mathbb{P}}(|Y(t)|)<\infty$ pour tout $t\in[0,T]$. On dit que $Y(t)$ est une martingale sous la mesure $\mathbb{P}$ si, pour tous $0\le t\le s\le T$,
>
> $$
> \mathbb{E}_t^{\mathbb{P}}[Y(s)] = Y(t) \quad \text{p.s.}
> $$

> #### Définition 1.1.2 (Espace $H^2$)
>
> On pose $\|\sigma(t,\omega)\|^2 = \operatorname{tr}(\sigma(t,\omega)\sigma(t,\omega)^\top)$. On dit que $\sigma$ appartient à $H^2$ si, pour tout $t\in[0,T]$,
>
> $$
> \mathbb{E}^{\mathbb{P}}\left[\int_0^t \|\sigma(s,\omega)\|^2\,\mathrm{d}s\right] < \infty.
> $$

> #### Théorème 1.1.3 (Propriétés de l'intégrale d'Itô)
>
> On définit $I(t)=\int_0^t \sigma(s,\omega)\,\mathrm{d}W_s$ et on suppose $\sigma\in H^2$. Alors :
>
> 1. $I(t)$ est $\mathcal{F}_t$-mesurable.
> 2. $I(t)$ est une martingale continue. En particulier $\mathbb{E}^{\mathbb{P}}[I(t)]=0$ pour tout $t\in[0,T]$.
> 3. $\mathbb{E}^{\mathbb{P}}[|I(t)|^2]=\mathbb{E}^{\mathbb{P}}\left[\int_0^t \|\sigma(s,\omega)\|^2\,\mathrm{d}s\right]<\infty$.
> 4. $\mathbb{E}^{\mathbb{P}}[I(t)I(s)^\top]=\mathbb{E}^{\mathbb{P}}\left[\int_0^{\min(t,s)} \sigma(u,\omega)\sigma(u,\omega)^\top\,\mathrm{d}u\right]$.

> #### Théorème 1.1.4 (Théorème de représentation des martingales)
>
> Si $Y$ est une martingale locale adaptée à la filtration générée par un mouvement brownien $W$, alors il existe un processus $\sigma$ tel que
>
> $$
> \mathrm{d}Y_t = \sigma(t,\omega)\,\mathrm{d}W_t.
> $$
>
> Si $Y$ est une martingale de carré intégrable, alors $\sigma\in H^2$.

> #### Théorème 1.1.5 (Formule d'Itô)
>
> Soit $f(t,x)$, $x=(x_1,\dots,x_p)^\top$, une fonction $C^{1,2}$ $f:[0,T]\times\mathbb{R}^p\to\mathbb{R}$. Soit $X(t)$ le processus d'Itô ci-dessus et $Y(t)=f(t,X(t))$. Alors $Y(t)$ est un processus d'Itô et on a :
>
> $$
> \begin{aligned}
> \mathrm{d}Y_t &= f_t(t,X_t)\,\mathrm{d}t + \nabla_x f(t,X_t)^\top \mu(t,X_t)\,\mathrm{d}t \\
> &\quad + \nabla_x f(t,X_t)^\top \sigma(t,X_t)\,\mathrm{d}W_t \\
> &\quad + \tfrac{1}{2}\operatorname{tr}\big(\sigma(t,X_t)\sigma(t,X_t)^\top D^2_x f(t,X_t)\big)\,\mathrm{d}t.
> \end{aligned}
> $$

## 1.2 Gains de trading et arbitrage

Nous considérons un investisseur qui suit une stratégie de trading portant sur les $p$ actifs $X_1,\dots,X_p$. La stratégie est caractérisée par un processus prévisible adapté $\phi(t,\omega)=(\phi_1(t,\omega),\dots,\phi_p(t,\omega))^\top$, où $\phi_i(t,\omega)$ désigne la position en $X_i$ au temps $t$. La valeur $\pi(t)$ de la stratégie au temps $t$ est (en omettant la dépendance en $\omega$) :

$$
\pi(t)=\phi(t)^\top X(t).
$$

Une stratégie est dite auto-financée si, pour tout $t\in[0,T]$,

$$
\pi(t)-\pi(0)=\int_0^t \phi(s)^\top \,\mathrm{d}X_s.
$$

> #### Définition 1.2.1 (Arbitrage)
>
> Une opportunité d'arbitrage est une stratégie auto-financée $\phi$ telle que $\pi(0)=0$ et, pour un certain $t\in[0,T]$,
>
> $$
> \pi(t) \ge 0 \quad \text{p.s.,} \quad \text{et }\; \mathbb{P}(\pi(t)>0)>0.
> $$

## 1.3 Mesures martingales équivalentes et arbitrage

> #### Théorème 1.3.1 (Radon–Nikodym)
>
> Soient $\mathbb{P}$ et $\widehat{\mathbb{P}}$ deux mesures de probabilité équivalentes sur l'espace mesurable commun $(\Omega,\mathcal{F})$. Il existe une variable aléatoire non négative (unique p.s.) $R$ telle que $\mathbb{E}^{\mathbb{P}}[R]=1$ et, pour tout $A\in\mathcal{F}$,
>
> $$
> \widehat{\mathbb{P}}(A)=\mathbb{E}^{\mathbb{P}}[R\,\mathbb{1}_A].
> $$
>
> Pour la suite, on associe à toute mesure $\widehat{\mathbb{P}}$ le processus densité
>
> $$
> \zeta(t)=\mathbb{E}_t^{\mathbb{P}}\left[\frac{\mathrm{d}\widehat{\mathbb{P}}}{\mathrm{d}\mathbb{P}}\right], \quad \forall t\in[0,T].
> $$
>
> On vérifie que $\zeta(t)$ est une martingale sous $\mathbb{P}$, avec $\zeta(0)=1$ et $\zeta(t)=\mathbb{E}_t^{\mathbb{P}}[\zeta(T)]$.
>
> Un simple exercice de conditionnement montre que pour toute variable $\mathcal{F}_T$-mesurable $Y(T)$, avec $R=\mathrm{d}\widehat{\mathbb{P}}/\mathrm{d}\mathbb{P}$,
>
> $$
> \mathbb{E}^{\widehat{\mathbb{P}}}[Y(T)\,|\,\mathcal{F}_t]=\mathbb{E}^{\mathbb{P}}\left[Y(T)\frac{\zeta(T)}{\zeta(t)}\,\Big|\,\mathcal{F}_t\right].
> $$
>
> On introduit maintenant le concept important de deflator (déflateur), un processus d'Itô strictement positif utilisé pour normaliser les prix d'actifs. Soit $D(t)$ le déflateur et posons $X^D(t)=(X_1(t)/D(t),\dots,X_p(t)/D(t))^\top$. On dit qu'une mesure $\mathbb{Q}^D$ est une mesure martingale équivalente induite par $D$ si $X^D(t)$ est une martingale sous $\mathbb{Q}^D$. Si $\mathbb{Q}^D$ est une mesure martingale, une stratégie auto-financée est dite admissible si
>
> $$
> \int_0^t \phi(s)^\top \,\mathrm{d}X^D_s
> $$
>
> est une martingale.

> #### Théorème 1.3.2 (Condition suffisante pour l'absence d'arbitrage)
>
> Restreignons-nous aux stratégies admissibles. Si existe un déflateur $D$ tel que le processus des prix défalutés admette une mesure martingale équivalente, alors il n'y a pas d'arbitrage.
>
> Si le déflateur est l'un des $p$ actifs, on l'appelle un numéraire.
>
> Supposons que $X_1$ soit strictement positif et puisse servir de numéraire. Supposons aussi qu'un déflateur $D$ ait été identifié comme dans le théorème ci-dessus. Comme $X_1(t)/D(t)$ est une martingale sous $\mathbb{Q}^D$, on peut définir une nouvelle mesure $\mathbb{Q}^{X_1}$ par la densité
>
> $$
> \zeta(t)=\frac{X_1(t)/D(t)}{X_1(0)/D(0)}.
> $$
>
> Pour une variable $\mathcal{F}_T$-mesurable $Y(T)$, on a alors :
>
> $$
> X_1(t)\,\mathbb{E}_t^{\mathbb{Q}^{X_1}}\left[\frac{Y(T)}{X_1(T)}\right]=D(t)\,\mathbb{E}_t^{\mathbb{Q}^{D}}\left[\frac{Y(T)}{D(T)}\right].
> $$
>
> En particulier, si $Y(t)/D(t)$ est une martingale sous $\mathbb{Q}^D$, alors $Y(t)/X_1(t)$ est une martingale sous $\mathbb{Q}^{X_1}$.

## 1.4 Valorisation des dérivés et marchés complets

A contingent claim d'échéance $T$ verse en $T$ une variable aléatoire $V(T)$ mesurable par rapport à $\mathcal{F}_T$ et n'effectue aucun paiement avant $T$.

Une stratégie de trading réplique le produit dérivé si $V(T)=\pi(T)$ p.s., et plus généralement $V(t)=\pi(t)$ pour tout $t\in[0,T]$.

Considérons un déflateur $D$ et supposons l'existence d'une mesure martingale équivalente $\mathbb{Q}^D$ induite par $D$. On en déduit que

$$
\frac{V(t)}{D(t)}=\mathbb{E}_t^{\mathbb{Q}^D}\left[\frac{V(T)}{D(T)}\right].
$$

> #### Théorème 1.4.1
>
> En l'absence d'arbitrage, un marché est complet si et seulement s'il existe un déflateur induisant une mesure martingale unique.

> #### Théorème 1.4.2 (Changement de numéraire)
>
> Considérons deux numéraires $N(t)$ et $M(t)$, induisant respectivement des mesures martingales équivalentes $\mathbb{Q}^N$ et $\mathbb{Q}^M$. Si le marché est complet, alors la densité de la dérivée de Radon–Nikodym reliant les deux mesures est donnée par
>
> $$
> \zeta(t)=\mathbb{E}_t^{\mathbb{Q}^N}\left[\frac{\mathrm{d}\mathbb{Q}^M}{\mathrm{d}\mathbb{Q}^N}\right]=\frac{M(t)/M(0)}{N(t)/N(0)}.
> $$

