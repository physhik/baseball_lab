# Jupyter notebook examples 

This instructions are such as a manual to follow to gain the stats made by this repo. 

Here, I present a bit of introductions about the new metrics considered at each examples. 


## 0. Setup 

The goal of this section is helping who do not know how to handle Python. 

Just prepare a Google account for Google drive and Google colab. And then follow the process and obtain the CSV format files you can open with Excel or any spread sheet program.    

Login your google account and 

Go to the colab link. https://colab.research.google.com/

It provides Jupyter notebook environment, and you can excute Python script and files. 

And then follow the instruction at [Setup.ipynb](https://github.com/physhik/baseball_lab/blob/master/practice/Setup.ipynb)


## 1. New metrics 

FIP (fielding independent pitching) could be one of most famous pitching stats in recent 10 years. So intuitive and not too hard to calculate. 

FIP formula has a constant term about 3.2 (varying up to the league ERA).

If I remember correctly, the constant comes from the bip and was suggested to be a fixed number because our understanding to batted ball was still unclear. 

Statcast now provides many good informations of the batted balls. Thus, we would want to really fielding independent pitching stats finally by using xwOBAcon or some other statcast stats else. I used xwOBAcon and rescaled the constant term to league ERA. You can see the formula at a python file in the Github repo. I temporarily named it nFIP in my project files. 

HR is also dependent on the environments such as the stadium, weathers, so we want to use barrels instead of HR as the represtative of the well-crushed hit. I named it xnFIP in my project files. 


One of the motives of this project is that FIP underestimates ground ball pitchers and the constant term about 3.2 is too big. Of course, strikeouts are really good. However, how do we estimate the value of weakly contacted ball in WAR?

The 2nd motive is ... if you check the variance of ERA of the players in the league compared to that of FIP. FIP's variance is much smaller. And the variances of xFIP, SIERA are much much smaller. That's why people thought FIP, xFIP, SIERA have some predictive potential. However, those stats just predict less boldly, and that's why they are wrong less to anticipate.

If the fixed number 3.2 varies, the variance of nFIP become larger and nFIP still yields better correlations to next year pitching stats. I think this caused by good property of the new stats to put the value in weak contacts. There are so much room to be adjusted in the stats, but hope this is a right direction to evaluate pitchers' ability. 

I also want to discuss if rescaling FIP to ERA makes sense. Why not RA? I want to call it rFIP here, and made derivatives too.  I prefer R because ER is influenced by error more than R. I wanted to avoid the situatioin HR, SO, BB are included only to FIP, not to ERA because of errors.

About xFIP, I think giving the same HR rate to the fly balls is rather old fashioned since the fly ball exit velocities have been measured.

## practice 2

Will be presented soon. 


## practice 4 

Other park correctors in baseball-reference considers the correction of the initial factor 

Initial factor of a park is computed by (Scored RUNs of home team at home per home game number + Allowed RUNs of home team at home per home game number )/ (SR of HT at away per AGN + AR of HT at away per AGN ). In other words, it presents how easy to make and allow runs at home.

The rough park factor can be calculated by (initial factor -1)/2 + 1. For example, if initial factor is 1.2, the rough park factor not considering small corrections is 1.1.

I recommend you to read the [this link](https://www.baseball-reference.com/about/parkadjust.shtml) before further discussion. The above link introduce how to compute the park factor for baseball reference. 

I want to discuss about the step 3, OPC (other park corrector).

"Make corrections for the fact that the other road parks' total difference from the league average is offset by the park rating of the club that is being rated"

BTW, it assumes the initial factors of the other parks are all identical, or have the same number of games with N-1 teams (N=30).

More details with formula can be found at [my personal blog](http://physhik.com/opc/).

However, it's slighty off because a mlb team have more games in the same division. This was already pointed out in other posts such as [this](https://www.reddit.com/r/Sabermetrics/comments/4kjlw9/are_park_factors_real/) 

I calculated the more precise OPC x Initial factor from the number of all the games of all the teams by web crawling mlb schedule.
