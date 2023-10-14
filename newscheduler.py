import random
import json
import itertools


class Scheduler:
    def __init__(self):
        self.intervals = []

    def add_interval(self, start_time, end_time, class_name, section):
        # Adds an interval to the list of intervals
        self.intervals.append((start_time, end_time, class_name, section))
        return True

    def find_optimal_schedule(self):
        # Sort intervals by end time
        sorted_intervals = sorted(self.intervals, key=lambda x: x[1])
        # Initialize variables
        n = len(sorted_intervals)
        dp = [1] * n
        prev = [-1] * n
        # Iterate over sorted intervals
        for i in range(1, n):
            for j in range(i):
                if sorted_intervals[j][1] <= sorted_intervals[i][0] and sorted_intervals[j][2] != sorted_intervals[i][2]:
                    if dp[j] + 1 > dp[i]:
                        dp[i] = dp[j] + 1
                        prev[i] = j
        # Find the maximum number of non-overlapping intervals
        max_intervals = max(dp)
        # Find the index of the last interval in the optimal schedule
        last_interval_index = dp.index(max_intervals)
        # Build the optimal schedule by backtracking through the prev array
        optimal_schedule = []
        while last_interval_index != -1:
            optimal_schedule.append(sorted_intervals[last_interval_index])
            last_interval_index = prev[last_interval_index]
        optimal_schedule.reverse()
        # Select only one section for each class in the optimal schedule
        selected_classes = set()
        final_schedule = []
        for interval in optimal_schedule:
            class_name = interval[2]
            sections = [i for i in optimal_schedule if i[2] == class_name]
            section = random.choice(sections)
            if class_name not in selected_classes:
                selected_classes.add(class_name)
                final_schedule.append(section)
        return final_schedule

def get_data():
    with open("data.json", "r") as f:
        data = json.load(f)
        return data
    
def find_sections(c):
    """
        Separates the lectures and recitations of a certain course into a hash map
        """
    course_to_sections = {}
    for course in c:
        course_to_sections[course["id"]] = {"LEC": [section for section in course["sections"] if section["activity"] == "LEC"], 
                                            "REC": [section for section in course["sections"] if section["activity"] == "REC"],}
    return course_to_sections

def find_activities(data, activity):
    """
        Given a dictionary of courses and their sections, returns a list of only the activities of a certain type (ex: LEC).
        
        Parameters:
        c_to_s (dict): A dictionary of courses and their sections.
        activity (str): The type of activity to filter by (ex: LEC).
        
        Returns:
        list: A list of activities of the specified type.
        """
    activities = []
    for key in data.keys():
        activities.append(data[key][activity])
    return activities

def find_lectures_on_day(lectures, day):
    """
        Finds all the lectures on a given day.

        Parameters:
            lectures (list): A list of lectures.
            day (str): The day to search for lectures on.

        Returns:
            list: A list of tuples containing the start time, end time, course code, and section ID for each lecture on the given day.
        """
    lectures_on_day = []
    for lecture in lectures:
        for section in lecture:
            for meeting in section["meetings"]:
                if meeting["day"] == day:
                    # Adds a randomizer to randomize the order they are fed to the scheduler
                    lectures_on_day.append((meeting["start"], meeting["end"]+0.001*random.random(), "-".join(section["id"].split("-")[0:2]), section["id"] ))
    return lectures_on_day

def check_overlap(intervals, new_interval):
    """
        Check if a new interval overlaps with any of the existing intervals.

        Parameters:
            intervals (list): A list of intervals, where each interval is a tuple of two integers representing the start and end points of the interval.
            new_interval (tuple): A tuple of two integers representing the start and end points of the new interval.

        Returns:
            bool: True if the new interval does not overlap with any of the existing intervals, False otherwise.
        """
    for interval in intervals:
        if new_interval[0] < interval[1] and new_interval[1] > interval[0]:
            return False
    return True
    
def schedule_to_section(schedules):
    """
        Given a list of schedules, returns a list of sections by stripping the time intervals from the schedule list.

        Parameters:
            schedules (list): A list of schedules.

        Returns:
            list: A list of sections.
        """
    sections = []
    for s in schedules:
        sections.append(s[3])
    return sections

def remove_duplicates(l):
    """
        Removes duplicates from a list.
        Example:
        remove_duplicates([1,1,1,3,5,7,7]) = [1,3,5,7]
        """
    newl = []
    [newl.append(x) for x in l if x not in newl]
    return newl

def choose_class_hash(l):
    """
        Given a list of section nodes, chooses one section per class from each schedule randomly.

        Parameters:
            l (list): A list of section nodes.

        Returns:
            list: A list of chosen sections, one per class.
        """
    hash = {}
    courses = []
    for node in l:
        class_name = "-".join(node.split("-")[0:2])
        if class_name not in hash.keys():
            hash[class_name] = [node]
        else:
            hash[class_name].append(node)
    for key in hash.keys():
        courses.append(random.choice(hash[key]))
    return courses

day_to_num = {"M": 0, "T": 1, "W": 2, "R": 3, "F": 4}

def check_if_schedule_possible(schedule, courses):
    """
        Given a schedule and a list of courses, checks if the schedule is possible by ensuring that there are no time conflicts
        between the meetings of the courses in the schedule.

        Parameters:
            schedule (list): A list of section IDs representing the courses in the schedule.
            courses (list): A list of dictionaries representing the courses, where each dictionary contains a list of sections.

        Returns:
            bool: True if the schedule is possible, False otherwise.
        """
    intervals = []
    for course in courses:
        for section in course:
            if section["id"] in schedule:
                for meeting in section["meetings"]:
                    intervals.append((day_to_num[meeting["day"]]+0.01*meeting["start"], day_to_num[meeting["day"]]+0.01*meeting["end"], section["id"]))
    intervals = sorted(intervals, key=lambda x: x[0])
    for i in range(len(intervals)):
        if i == 0:
            continue
        if intervals[i][0] < intervals[i-1][1]:
            return False
    return True

def scheduler_for_day(lectures, day):
    """
        Takes a list of lectures and a day of the week, and returns a list of unique schedules for that day.
        The schedules are generated by taking 10 samples of possible schedules based on the dynamic programming algorithm.
        """
    day_classes = find_lectures_on_day(lectures, day)
    scheduler = Scheduler()
    for day_class in day_classes:
        scheduler.add_interval(day_class[0], day_class[1], day_class[2], day_class[3])
    day_schedules = []
    for _ in range(10):
        day_schedules.append(scheduler.find_optimal_schedule())
    day_schedules_unique = remove_duplicates(day_schedules)
    return day_schedules_unique

def add_recs_to_schedule(schedule, recs,lectures):
    """
        Bruteforces recitations into the schedule based on the lectures.

        Parameters:
            schedule (list): A list of strings representing the current schedule.
            recs (list): A list of lists, where each inner list contains dictionaries representing recitation sections for a course.
            lectures (list): A list of lists, where each inner list contains dictionaries representing lecture sections for a course.

        Returns:
            list: A list of strings representing the updated schedule with recitation sections added.

        """
    newschedule = schedule
    for course in recs:
        if course != []:
            course_name = "-".join(course[0]["id"].split("-")[0:2])
            schedule_names = list(map(lambda x: "-".join(x.split("-")[0:2]), schedule))
            if course_name in schedule_names:
                for section in course:
                    if check_if_schedule_possible(schedule+[section["id"]], recs+lectures):
                        newschedule.append(section["id"])
                        break
    return newschedule

def find_possible_schedules(count=None):
    """
        Given a list of courses, returns a list of all possible schedules that can be made from those courses.
        If a count is specified, returns only schedules with that many courses.
    """
    data = get_data()
    c_to_s = find_sections(data)
    lectures = find_activities(c_to_s, "LEC")
    recs = find_activities(c_to_s, "REC")
    
    monday_schedules = scheduler_for_day(lectures, "M")
    tues_schedules = scheduler_for_day(lectures, "T")
    wed_schedules = scheduler_for_day(lectures, "W")
    thurs_schedules = scheduler_for_day(lectures, "R")
    fri_schedules = scheduler_for_day(lectures, "F")

    possible_mwf = []
    for i in range(len(monday_schedules)):
       for j in range(len(wed_schedules)):
           for k in range(len(fri_schedules)):
                  possible_mwf.append(monday_schedules[i] + wed_schedules[j] + fri_schedules[k])
    
    possible_tr = []
    for i in range(len(tues_schedules)):
        for j in range(len(thurs_schedules)):
                possible_tr.append(tues_schedules[i] + thurs_schedules[j])

    total_schedules = []
    for i in range(len(possible_tr)):
        for j in range(len(possible_mwf)):
                total_schedules.append(possible_tr[i] + possible_mwf[j])
    

    courses = list(map(schedule_to_section, total_schedules))
    courses_unique = list(map(remove_duplicates, courses))

    choose = list(map(choose_class_hash, courses_unique))
    choose = [schedule for schedule in choose if check_if_schedule_possible(schedule, lectures)]
    if count != None:
        combinations = []
        for i in range(len(choose)):
            [combinations.append(list(c)) for c in itertools.combinations(choose[i], count) if c not in combinations]
    else:
        combinations = choose
    choose = [add_recs_to_schedule(schedule, recs, lectures) for schedule in combinations]
    choose = sorted(choose, key=lambda x: len(x))
    return choose

credit_limit = 5
schedules = []
for i in range(15):
    schedules.append(find_possible_schedules(credit_limit))
schedules = sorted(schedules, key=lambda x: -len(x))
print(schedules[0][0:5])
# Obviously will return course objects later