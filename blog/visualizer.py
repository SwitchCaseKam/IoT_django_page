import datetime
import numpy as np
import plotly
import plotly.graph_objs as go

from .models import *
from django.utils import timezone
from django.db.models import Avg, Sum, F


class Visualizer:
    def __init__(self, user, auto_open=False, minutes_delta=15, minutes_grid=60, grid_steps=10, grid_pulse=5.0, grid_alcohol=0.2, min_daily_values=10, min_monthly_values=100, min_2d_values=200, min_3d_values=500):
        self.user = user
        self.auto_open = auto_open
        self.grid_steps = grid_steps
        self.grid_pulse = grid_pulse
        self.grid_alcohol = grid_alcohol
        self.time_delta = datetime.timedelta(minutes=minutes_delta)
        self.grid_time = datetime.timedelta(minutes=minutes_grid)
        
        self.min_daily_values = min_daily_values
        self.min_monthly_values = min_monthly_values
        self.min_2d_values = min_2d_values
        self.min_3d_values = min_3d_values

    def plot_all(self):
        analysis = self.plot_analysis()
        d = {'last_steps': self.plot_last_steps(),
             'last_pulse': self.plot_last_pulse(),
             'last_alcohol': self.plot_last_alcohol(),
             'steps_in_time': self.plot_steps(),
             'pulse_in_time': self.plot_pulse(),
             'alcohol_in_time': self.plot_alcohol(),
             'activity': self.plot_activity(),
             'analysis2d': analysis[0],
             'analysis3d': analysis[1]}
        return d

    def get_last_data(self, model, days_nr=1, now=None, prev=None):
        if now is None:
            now = timezone.now()
        if prev is None:
            prev = now - datetime.timedelta(days=days_nr)
        return model.objects.using('new_smartband_db'). \
            filter(user=self.user). \
            filter(timestamp__range=(prev, now)).all()

    def plot(self, data, title, xaxis, yaxis, filename="temp.html", showlegend=False):
        layout = go.Layout(title=title, xaxis=xaxis, yaxis=yaxis, showlegend=showlegend)
        figure = go.Figure(data=data, layout=layout)
        if self.auto_open:
            plotly.offline.plot(figure, auto_open=True, filename=filename)
        else:
            div = plotly.offline.plot(figure, auto_open=False, output_type='div')
            return div
	
    def daily_grid(self, model, name, func):    
        now = timezone.now()
        prev = now - datetime.timedelta(days=1)
        data = self.get_last_data(model, now=now, prev=prev)
        if len(data) < self.min_daily_values:
            return None, None, None
        hist = data.values("timestamp__date", "timestamp__hour").annotate(data_agg=func(name))
        hist_x = [None for _ in range(24)]
        hist_y = [None for _ in range(24)]
        for h in hist:
            ind = (h["timestamp__hour"] - now.hour) % 24
            y = h["data_agg"]
            x = datetime.datetime(year=h["timestamp__date"].year, 
                                  month=h["timestamp__date"].month,
                                  day=h["timestamp__date"].day,
                                  hour=h["timestamp__hour"],
                                  minute=30,
                                  tzinfo=now.tzinfo)
            hist_x[ind] = x
            hist_y[ind] = y
        print("now", now.hour)
        print("x", hist_x)
        print("y", hist_y)
        return data.order_by('timestamp'), hist_x, hist_y
	
    def monthly_grid(self, model, name, func):    
        now = timezone.now()
        prev = now - datetime.timedelta(days=31)
        data = self.get_last_data(model, now=now, prev=prev)
        if len(data) < self.min_monthly_values:
            return None, None
        hist = data.values("timestamp__date").annotate(data_agg=func(name))
        hist_x = [None for _ in range(31)]
        hist_y = [None for _ in range(31)]
        for h in hist:
            h_datetime = datetime.datetime.combine(h["timestamp__date"], datetime.datetime.min.time(), now.tzinfo)
            ind = (h_datetime - now).days % 31
            y = h["data_agg"]
            x = h["timestamp__date"]
            hist_x[ind] = x
            hist_y[ind] = y
        return hist_x, hist_y

    def plot_last_steps(self):
        #activities = self.get_last_data(Activity)
        activities, hist_x, hist_y = self.daily_grid(model=Activity, name="steps", func=Sum)
        if activities is None or hist_x is None or hist_y is None:
            return None
        trace1 = go.Scatter(x=[a.timestamp for a in activities],
                            y=[a.steps for a in activities],
                            mode="markers",
                            marker={"color": "red"})
        trace2 = go.Bar(x=hist_x,
                        y=hist_y,
                        marker={"color": "blue"})
        return self.plot(data=[trace1, trace2],
                         title="Steps in last day",
                         xaxis={'title': 'time'},
                         yaxis={'title': 'steps'},
                         filename="last_steps.html")

    def plot_last_pulse(self):
        #activities = self.get_last_data(Activity)
        activities, hist_x, hist_y = self.daily_grid(model=Activity, name="pulse", func=Avg)
        if activities is None or hist_x is None or hist_y is None:
            return None
        trace1 = go.Scatter(x=[a.timestamp for a in activities],
                           y=[a.pulse for a in activities],
                           mode="markers",
                            marker={"color": "red"})
        trace2 = go.Scatter(x=hist_x,
                            y=hist_y,
                            mode="lines",
                            marker={"color": "blue"})
        return self.plot(data=[trace1, trace2],
                         title="Pulse in last day",
                         xaxis={'title': 'time'},
                         yaxis={'title': 'pulse'},
                         filename="last_pulse.html")

    def plot_last_alcohol(self):
        #drinking = self.get_last_data(Drinking)
        drinking, hist_x, hist_y = self.daily_grid(model=Drinking, name="alcohol", func=Avg)
        if drinking is None or hist_x is None or hist_y is None:
            return None
        trace1 = go.Scatter(x=[a.timestamp for a in drinking],
                            y=[a.alcohol for a in drinking],
                            mode="markers",
                            marker={"color": "red"})
        trace2 = go.Scatter(x=hist_x,
                            y=hist_y,
                            mode="lines",
                            marker={"color": "blue"})
        return self.plot(data=[trace1, trace2],
                         title="Alcohol in last day",
                         xaxis={'title': 'time'},
                         yaxis={'title': 'alcohol'},
                         filename="last_alcohol.html")

    def plot_monthly_steps(self):
        #activities = self.get_last_data(Activity)
        hist_x, hist_y = self.monthly_grid(model=Activity, name="steps", func=Sum)
        if hist_x is None or hist_y is None:
            return None
        trace2 = go.Bar(x=hist_x,
                        y=hist_y)
        return self.plot(data=[trace2],
                         title="Steps in last month",
                         xaxis={'title': 'time'},
                         yaxis={'title': 'steps'},
                         filename="monthly_steps.html")

    def plot_monthly_pulse(self):
        #activities = self.get_last_data(Activity)
        hist_x, hist_y = self.monthly_grid(model=Activity, name="pulse", func=Avg)
        if hist_x is None or hist_y is None:
            return None
        trace2 = go.Bar(x=hist_x,
                        y=hist_y)
        return self.plot(data=[trace2],
                         title="Pulse in last month",
                         xaxis={'title': 'time'},
                         yaxis={'title': 'pulse'},
                         filename="monthly_pulse.html")

    def plot_monthly_alcohol(self):
        #drinking = self.get_last_data(Drinking)
        hist_x, hist_y = self.monthly_grid(model=Drinking, name="alcohol", func=Avg)
        if hist_x is None or hist_y is None:
            return None
        trace2 = go.Bar(x=hist_x,
                        y=hist_y)
        return self.plot(data=[trace2],
                         title="Alcohol in last month",
                         xaxis={'title': 'time'},
                         yaxis={'title': 'alcohol'},
                         filename="monthly_alcohol.html")

    @staticmethod
    def grid2d(x, y, grid_x):
        d_lists = {}
        for xx, yy in zip(x, y):
            x_int = round(xx/grid_x)
            if x_int in d_lists.keys():
                d_lists[x_int].append(yy)
            else:
                d_lists[x_int] = [yy]
        new_x = []
        new_y = []
        for k in d_lists.keys():
            k_list = d_lists[k]
            new_x.append(k*grid_x)
            new_y.append(float(sum(k_list))/len(k_list))
        return new_x, new_y

    @staticmethod
    def grid3d(x, y, z, grid_x, grid_y):
        d_lists = {}
        x_int_min = 0
        x_int_max = 0
        y_int_min = 0
        y_int_max = 0
        for xx, yy, zz in zip(x, y, z):
            x_int = round(xx / grid_x)
            y_int = round(yy / grid_y)
            x_int_min = min(x_int_min, x_int)
            x_int_max = max(x_int_max, x_int)
            y_int_min = min(y_int_min, y_int)
            y_int_max = max(y_int_max, y_int)
            if (x_int, y_int) in d_lists.keys():
                d_lists[(x_int, y_int)].append(zz)
            else:
                d_lists[(x_int, y_int)] = [zz]
        new_x = np.array(list(range(x_int_min, x_int_max + 1))) * grid_x
        new_y = np.array(list(range(y_int_min, y_int_max + 1))) * grid_y
        new_z = np.zeros(shape=(len(new_y), len(new_x)))
        new_z[:] = np.NaN
        for k in d_lists.keys():
            k_list = d_lists[k]
            ind_x = k[0] - x_int_min
            ind_y = k[1] - y_int_max
            new_z[ind_y, ind_x] = float(sum(k_list)) / len(k_list)
        return new_x, new_y, new_z

    def plot_analysis(self):
        drink_query = Drinking.objects.using('new_smartband_db').filter(user=self.user).order_by('alcohol').all()
        act_query = Activity.objects.using('new_smartband_db').filter(user=self.user).order_by('steps').all()
        x = []
        y = []
        z = []
        for drink in drink_query:
            alco = drink.alcohol
            alco_time = drink.timestamp
            act_filtered = act_query.filter(timestamp__range=(alco_time - self.time_delta/2, alco_time + self.time_delta/2))
            '''print(drink)
            for a in act_filtered:
                print("\t", a)'''
            if len(act_filtered) > 0:
                mean_steps = act_filtered.aggregate(Avg('steps'))['steps__avg']
                mean_pulse = act_filtered.aggregate(Avg('pulse'))['pulse__avg']
                x.append(alco)
                y.append(mean_steps)
                z.append(mean_pulse)
        if len(drink_query) < self.min_3d_values or len(act_query) < self.min_3d_values:
            return None, None
        analysis2d = self.plot_analysis2d(x, y)
        analysis3d = self.plot_analysis3d(x, y, z)
        return analysis2d, analysis3d

    def plot_analysis2d(self, x, y):
        new_x, new_y = self.grid2d(x, y, self.grid_alcohol)
        trace = go.Scatter(x=new_x,
                           y=new_y,
                           mode="lines+markers")
        return self.plot(data=[trace],
                         title='steps (alcohol)',
                         xaxis={'title': 'alcohol'},
                         yaxis={'title': 'steps'},
                         filename='analysis2d.html')

    def plot_analysis3d(self, x, y, z):
        new_x, new_y, new_z = self.grid3d(x, y, z, self.grid_alcohol, self.grid_steps)
        trace = go.Heatmap(
            x=new_x,
            y=new_y,
            z=new_z,
            colorscale='Jet',
            colorbar={'title': 'pulse'})
        return self.plot(data=[trace],
                         title='pulse (alcohol, steps)',
                         xaxis={'title': 'alcohol'},
                         yaxis={'title': 'steps'},
                         filename='analysis3d.html',
                         showlegend=True)

    def plot_activity(self):
        act_query = Activity.objects.using('new_smartband_db').filter(user=self.user).order_by('steps').all()
        if len(act_query) < self.min_2d_values:
            return None
        x = [a.steps for a in act_query]
        y = [a.pulse for a in act_query]
        new_x, new_y = self.grid2d(x, y, self.grid_steps)
        trace = go.Scatter(x=new_x,
                           y=new_y,
                           mode="lines+markers")
        return self.plot(data=[trace],
                         title='pulse (steps)',
                         xaxis={'title': 'steps'},
                         yaxis={'title': 'pulse'},
                         filename='activity.html')

    def get_grid_time_list(self):
        gtime = datetime.datetime(year=2000, month=1, day=1)
        next_day = datetime.datetime(year=2000, month=1, day=2)
        times = []
        while gtime < next_day:
            times.append(gtime.time())
            gtime += self.grid_time
        return np.array(times)

    def plot_week(self, timestamps, values, colorbar, title, xaxis, yaxis, filename="temp.html"):
        if len(values) < self.min_3d_values:
            return None
        x = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        y = self.get_grid_time_list()
        d_lists = {}
        for t, v in zip(timestamps, values):
            t_weekday_ind = t.weekday()
            t_time = t.time()
            if t_time == datetime.time(hour=0, minute=0):
                t_time_ind = 0
            else:
                t_time_ind = np.searchsorted(y, t_time) - 1
            ind = (t_weekday_ind, t_time_ind)
            if ind not in d_lists.keys():
                d_lists[ind] = [v]
            else:
                d_lists[ind].append(v)
        z = np.zeros(shape=(len(y), len(x)))
        z[:] = np.NaN
        for k in d_lists.keys():
            k_list = d_lists[k]
            ind_x = k[0]
            ind_y = k[1]
            z[ind_y, ind_x] = float(sum(k_list)) / len(k_list)

        trace = go.Heatmap(
            x=x,
            y=y,
            z=z,
            colorscale='Jet',
            colorbar={'title': colorbar})
        return self.plot(data=[trace],
                         title=title,
                         xaxis=xaxis,
                         yaxis=yaxis,
                         filename=filename,
                         showlegend=True)

    def plot_steps(self):
        act_query = Activity.objects.using('new_smartband_db').filter(user=self.user).all()
        timestamps = [a.timestamp for a in act_query]
        values = [a.steps for a in act_query]
        return self.plot_week(timestamps, values,
                              colorbar='steps',
                              title='steps in time',
                              xaxis={'title': 'weekday'},
                              yaxis={'title': 'hour'},
                              filename='steps_in_time.html')

    def plot_pulse(self):
        act_query = Activity.objects.using('new_smartband_db').filter(user=self.user).all()
        timestamps = [a.timestamp for a in act_query]
        values = [a.pulse for a in act_query]
        return self.plot_week(timestamps, values,
                              colorbar='pulse',
                              title='pulse in time',
                              xaxis={'title': 'weekday'},
                              yaxis={'title': 'hour'},
                              filename='pulse_in_time.html')

    def plot_alcohol(self):
        drink_query = Drinking.objects.using('new_smartband_db').filter(user=self.user).all()
        timestamps = [d.timestamp for d in drink_query]
        values = [d.alcohol for d in drink_query]
        return self.plot_week(timestamps, values,
                              colorbar='alcohol',
                              title='alcohol in time',
                              xaxis={'title': 'weekday'},
                              yaxis={'title': 'hour'},
                              filename='alcohol_in_time.html')

