"""Line of Balance"""

from .utils import excel_table, plot_all_activities

# pylint: disable-msg=C0103

class LineOfBalance:
    """LINE OF BALANCE"""

    def __init__(self,
                 activity_names,
                 man_hours_per_unit,
                 men_per_gang,
                 buffer_time,
                 productivity_rate,
                 number_of_units_to_produce,
                 hours_per_day,
                 days_per_week,
                 ymin=0):

        self.activity_names = activity_names
        self.man_hours_per_unit = man_hours_per_unit
        self.men_per_gang = men_per_gang
        self.buffer_time = buffer_time
        self.productivity_rate = productivity_rate
        self.number_of_units_to_produce = number_of_units_to_produce
        self.hours_per_day = hours_per_day
        self.days_per_week = days_per_week
        self.number_of_activities = len(self.activity_names)
        self.ymax = self.number_of_units_to_produce
        self.ymin = ymin

    def theoretical_gang_size(self):
        """Compute theoretical gang sizes"""
        theo_g_size = [(self.productivity_rate*each) /
                       (self.hours_per_day*self.days_per_week)
                       for each in self.man_hours_per_unit]
        return [round(x, 2) for x in theo_g_size]

    def actual_gang_size(self):
        """Compute actual gang sizes"""
        actual_gang_size = [2 * x for x in self.men_per_gang]

        for idx, item in enumerate(actual_gang_size):
            old_gang_size = item

            for j in range(3, 6):
                new_gang_size = j * self.men_per_gang[idx]

                if abs(old_gang_size - self.theoretical_gang_size()[idx]) >=\
                abs(new_gang_size - self.theoretical_gang_size()[idx]):
                    old_gang_size = new_gang_size

            actual_gang_size[idx] = old_gang_size
        return list([round(x, 2) for x in actual_gang_size])

    def actual_output_rate(self):
        """Compute actual output rates"""
        act_out = [self.productivity_rate * (x/y)
                   for x, y in zip(self.actual_gang_size(),
                                   self.theoretical_gang_size())]
        return list([round(x, 2) for x in act_out])

    def activity_duration_per_unit(self):
        """Compute actual duration per unit"""
        adpu = [mhpu / (mpg * self.hours_per_day)
                for  mhpu, mpg in zip(self.man_hours_per_unit, self.men_per_gang)]
        return [round(x, 2) for x in adpu]

    def start_first_to_start_last(self):
        """Docstring"""
        sftl = [(self.number_of_units_to_produce - 1) * self.days_per_week /
                each for each in self.actual_output_rate()]
        return [round(x, 2) for x in sftl]

    def start_end(self):
        """Compute four last columns concurrently. First section start and end"""
        start_first = [1]
        end_first = [self.activity_duration_per_unit()[0]]

        start_last = [self.start_first_to_start_last()[0]]
        end_last = [start_last[0] + end_first[0]]

        for i in range(1, self.number_of_activities):

            if self.actual_output_rate()[i] < self.actual_output_rate()[i-1]:
                # place buffer at bottom
                start_first.insert(i, end_first[i-1] + self.buffer_time)
                end_first.insert(i, start_first[i] + self.activity_duration_per_unit()[i])

                start_last.insert(i, start_first[i] +\
                self.start_first_to_start_last()[i])
                end_last.insert(i, start_last[i] + self.activity_duration_per_unit()[i])

            elif self.actual_output_rate()[i] > self.actual_output_rate()[i-1]:
                # place buffer at bottom
                start_last.insert(i, end_last[i-1] + self.buffer_time)
                end_last.insert(i, start_last[i] + self.activity_duration_per_unit()[i])

                start_first.insert(i, start_last[i] - \
                self.start_first_to_start_last()[i])
                end_first.insert(i, start_first[i] + self.activity_duration_per_unit()[i])

        return [round(x, 2) for x in start_first], [round(x, 2) for x in end_first],\
        [round(x, 2) for x in start_last], [round(x, 2) for x in end_last]

    def start_on_first_section(self):
        """Start on first section for activity"""
        return self.start_end()[0]

    def end_on_first_section(self):
        """End on first section for activity"""
        return self.start_end()[1]

    def start_on_last_section(self):
        """Start on last section for activity"""
        return self.start_end()[2]

    def end_on_last_section(self):
        """End on last section for activity"""
        return self.start_end()[3]

    def arrange_values(self):
        """Arrange the values in tabular format"""

        values = [[a, b, c, d, e, f, g, h, i, j, k, l]
                  for a, b, c, d, e, f, g, h, i, j, k, l in
                  zip(self.activity_names,
                      self.man_hours_per_unit,
                      self.men_per_gang,
                      self.theoretical_gang_size(),
                      self.actual_gang_size(),
                      self.actual_output_rate(),
                      self.activity_duration_per_unit(),
                      self.start_first_to_start_last(),
                      self.start_on_first_section(),
                      self.end_on_first_section(),
                      self.start_on_last_section(),
                      self.end_on_last_section())]
        return values

    def column_headings(self): # add **kwargs to take additional columns
        """Column headings"""
        columns = ("Activity",
                   "Man hours per unit",
                   "Men per gang",
                   "Theoretical gang size",
                   "Actual gang size",
                   "Actual output rate",
                   "Activity duration per unit",
                   "Start on first section to start on last section",
                   "Start on first section",
                   "End on first section",
                   "Start on last section",
                   "End on last section")
        return columns

    def generate_plot_points(self):
        """Generate plot points"""
        return [(a, b, c, d, e) for a, b, c, d, e in
                zip(self.activity_names,
                    self.start_on_first_section(),
                    self.end_on_first_section(),
                    self.start_on_last_section(),
                    self.end_on_last_section())]

    def generate_curve(self):
        """Generate the line of balance curve"""
        points_to_plot = self.generate_plot_points()
        plot_all_activities(points_to_plot, self.ymin, self.ymax)

    def project_duration(self):
        """Total project duration"""
        return self.generate_plot_points()[-1][4]+1

    def create_table(self):
        """Create table from object"""
        heads = self.column_headings()
        vals = self.arrange_values()
        excel_table(heads, vals)

def main():
    """Main with default arguments"""
    activity_names = ['A', 'B', 'C', 'D', 'E']
    man_hours_per_unit = [100, 350, 60, 200, 150]
    men_per_gang = [4, 6, 2, 5, 8]
    buffer_time = 5
    productivity_rate = 3
    number_of_units_to_produce = 20
    hours_per_day = 8
    days_per_week = 5

    line_object = LineOfBalance(activity_names,
                                man_hours_per_unit,
                                men_per_gang,
                                buffer_time,
                                productivity_rate,
                                number_of_units_to_produce,
                                hours_per_day,
                                days_per_week)
    line_object.generate_curve()
    line_object.create_table()
    return line_object

if __name__ == "__main__":
    main()
