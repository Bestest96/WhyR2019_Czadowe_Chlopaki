def get_df_by_type(places_df, pop_times_df, place_type):
    places_by_type = places_df[places_df.type == place_type]
    pop_times_by_type = pop_times_df[pop_times_df.place_id.isin(places_by_type.place_id)]
    return places_by_type, pop_times_by_type


def get_pop_by_time(pop_times_df, hour, day):
    has_time = (pop_times_df.hour == hour) & (pop_times_df.day == day)
    pop_times_by_time = pop_times_df[has_time]
    return pop_times_by_time


def get_places_pop(places_df, pop_times_df, hour, day):
    pop_by_time = get_pop_by_time(pop_times_df, hour, day)
    pop_by_time = pop_by_time[['place_id', 'occupancy_index']].groupby(['place_id']).mean()
    return pop_by_time.join(places_df.set_index('place_id'))

