from collections import defaultdict
from itertools import permutations, cycle
import itertools
import random
from otree.api import (
    models, BaseGroup, BasePlayer, BaseSubsession, BaseConstants, widgets
)
from .helpers import get_strings

def likert_field(label, verbose_name):
    return models.IntegerField(
        label=label,
        verbose_name=verbose_name,
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, 'Strongly disagree'],
            [2, 'Disagree'],
            [3, 'Somewhat disagree'],
            [4, 'Neither agree nor disagree'],
            [5, 'Somewhat agree'],
            [6, 'Agree'],
            [7, 'Strongly agree']
        ]
    )


class C(BaseConstants):
    NAME_IN_URL = 'random_task_order'
    PLAYERS_PER_GROUP = 3
    TREATEMENTS = ['VCG', 'BordaCount', 'TTC']
    NUM_ROUNDS = 3 
    MAX_BID = 100
    MIN_BID = 0
    TIMEOUT_INITIAL = 720
    STARTTIME_INITIAL = 0
    POINTS_TO_EUR = 0.05
    SHOWUP_FEE = 3
    strings = get_strings()

    INTEGRITY_VN = 'I believe that the matching app would remain consistent and predictable.'
    COMPETENCY_VN = 'I believe that the matching app is very capable of making effective decisions.'
    BENEVOLENCE_VN = 'I believe that the matching app would act in my best interest.'

    SATISFACTION_VN = 'I am satisfied with my matching.'
    DISSATISFACTION_VN = 'I am dissatisfied with my matching.'
    FAIRNESS_VN = 'My matching was fair.'
    UNDERSTANDING_VN = 'I understood the process by which the matching was made.'
    AGREEMENT_VN = 'I agree with the matching.'
    APPROPRIATENESS_VN = 'The factors considered by the matching app were appropriate.'

    likert_7 = [
        [1, 'Strongly disagree'],
        [2, 'Disagree'],
        [3, 'Somewhat disagree'],
        [4, 'Neither agree nor disagree'],
        [5, 'Somewhat agree'],
        [6, 'Agree'],
        [7, 'Strongly agree']
    ]

    effort = [
        [1, '1: Very, very low mental effort'],
        [2, '2: Very low mental effort'],
        [3, '3: Low mental effort'],
        [4, '4: Rather low mental effort'],
        [5, '5: Neither low nor high mental effort'],
        [6, '6: Rather high mental effort'],
        [7, '7: High mental effort'],
        [8, '8: Very high mental effort'],
        [9, '9: Very, very high mental effort']
    ]

    borda_choices = [
        [1, '3 points'],
        [2, '2 points'],
        [3, '1 point'],
    ]

    ttc_choices = [
            [1, '1st choice'],
            [2, '2nd choice'],
            [3, '3rd choice'],
        ]


import itertools

class Group(BaseGroup):
    treatment_order = models.StringField()
    def vcg_allocation(self):
        bids = defaultdict(dict)

        # Get the bids from each player for each room
        for player in self.get_players():
            bids[player.id_in_group]['X'] = player.bid_room_X
            bids[player.id_in_group]['Y'] = player.bid_room_Y
            bids[player.id_in_group]['Z'] = player.bid_room_Z

        # find the allocation that maximizes the total bid
        players = list(bids.keys())
        rooms = ['X', 'Y', 'Z']
        max_total = -1

        for allocation in itertools.permutations(rooms):
            total = sum(bids[player][room] for player, room in zip(players, allocation))
            if total > max_total:
                max_total = total
                optimal_allocation = allocation

        for player, room in zip(self.get_players(), optimal_allocation):
            player.assigned_room = room

            bids_ = [
                (player.bid_room_X, 'X'),
                (player.bid_room_Y, 'Y'),
                (player.bid_room_Z, 'Z'),
            ]

            bids_.sort(reverse=True)

            # Map from rank to points
            rank_to_points = {0: 100, 1: 80, 2: 60}

            # Find the ranks of the assigned room and handle equal bids
            assigned_room_ranks = [i for i, bid in enumerate(bids_) if bid[1] == player.assigned_room]

            # Determine if there is a tie by checking if there are other rooms with the same bid as the assigned room
            tie_ranks = [i for i, bid in enumerate(bids_) if bid[0] == bids_[assigned_room_ranks[0]][0]]

            # If there's a tie, average the points of all the tied ranks; otherwise, just give the points for the assigned room's rank
            if len(tie_ranks) > 1:
                player.points = int(sum(rank_to_points.get(rank, 0) for rank in tie_ranks) / len(tie_ranks))
            else:
                player.points = rank_to_points[assigned_room_ranks[0]]


        # Calculate the payment for each player
        for player in self.get_players():
            others = [p for p in players if p != player.id_in_group]
            max_total_without_player = -1

            # print(f"\nAll possible allocations and total bids without Player {player.id_in_group}:")
            for allocation in itertools.permutations(rooms, len(others)):
                total = sum(bids[p][room] for p, room in zip(others, allocation))
                # print(f"Allocation: {dict(zip(others, allocation))}, Total bid: €{total}")
                if total > max_total_without_player:
                    max_total_without_player = total
                    optimal_allocation_without_player = allocation

            # print(f"\nOptimal Allocation without Player {player.id_in_group}:")
            # for other, room in zip(others, optimal_allocation_without_player):
            #     print(f"Player {other} gets room {room}")

            # Player is pivotal if the room assignment changes for at least one other player when they don't participate
            allocation_without_player = tuple(
                room for p, room in zip(players, optimal_allocation) if p != player.id_in_group)
            if any(room != room_without for room, room_without in
                   zip(optimal_allocation_without_player, allocation_without_player)):
                player.payment_vcg = max_total_without_player - (
                        max_total - bids[player.id_in_group][player.assigned_room])
                if player.payment_vcg > 0:
                    player.pivotal = 1
            else:
                player.payment_vcg = 0
            # print(f"\nPlayer {player.id_in_group} is pivotal: {player.pivotal}")
            # print(player)
            player.subtracted_points_vcg = float(player.payment_vcg)
            player.points = player.points - float(player.subtracted_points_vcg)


    def assign_rooms_borda(self):
        players = self.get_players()
        rooms = ['X', 'Y', 'Z']
        points_per_rank = {1: 100, 2: 80, 3: 60}

        for room in rooms:
            # Calculate total points for each room
            room_points = {player.id_in_group: (4 - int(getattr(player, f'borda_count_room_{room}') or 0))
                        for player in players}

            # Assign room to the player with the highest points for this room
            highest_scoring_player_id = max(room_points, key=room_points.get)
            highest_scoring_player = next(p for p in players if p.id_in_group == highest_scoring_player_id)
            highest_scoring_player.assigned_room = room
            highest_scoring_player.assigned_room_rank = int(getattr(highest_scoring_player, f'borda_count_room_{room}'))

            highest_scoring_player.points = points_per_rank[int(getattr(highest_scoring_player, f'borda_count_room_{room}'))]

            # Remove assigned player from further consideration
            players.remove(highest_scoring_player)

    def assign_rooms_ttc(self):
        players = self.get_players()
        unassigned_players = players.copy()
        unassigned_rooms = ['X', 'Y', 'Z']
        points_per_rank = {1: 100, 2: 80, 3: 60}

        while unassigned_players:
            starting_player = unassigned_players[0]
            cycle = []
            current_player = starting_player

            while current_player not in cycle:
                cycle.append(current_player)
                favorite_room = current_player.get_favorite_room(unassigned_rooms)
                current_player = self.get_highest_ranking_player(favorite_room, unassigned_players)

            for player in cycle:
                favorite_room = player.get_favorite_room(unassigned_rooms)
                player.assigned_room = favorite_room
                player.assigned_room_rank = int(getattr(player, f'ttc_room_{favorite_room}'))
                player.points = points_per_rank.get(player.assigned_room_rank, 0)
                unassigned_players.remove(player)
                unassigned_rooms.remove(favorite_room)

    def get_highest_ranking_player(self, room, unassigned_players):
        # Create a list of tuples (player, rank) for the given room
        player_rankings = [(p, getattr(p, f'ttc_room_{room}')) for p in unassigned_players]

        # Sort the list by rank and return the player with the highest rank
        player_rankings.sort(key=lambda x: x[1])
        return player_rankings[0][0]
    
    def set_payoffs_1(self):
        for player in self.get_players():
            # choose a random round to pay
            player.part_to_pay = random.randint(1, C.NUM_ROUNDS)
            player.payoff = player.in_round(player.part_to_pay).points
            player.payoff_points = player.in_round(player.part_to_pay).points


class Player(BasePlayer):
    part_to_pay = models.IntegerField()
    start_time_VCG = models.IntegerField(initial=C.STARTTIME_INITIAL)
    start_time_TTC = models.IntegerField(initial=C.STARTTIME_INITIAL)
    start_time_Borda = models.IntegerField(initial=C.STARTTIME_INITIAL)

    timeout_VCG = models.IntegerField(initial=C.TIMEOUT_INITIAL)
    timeout_TTC = models.IntegerField(initial=C.TIMEOUT_INITIAL)
    timeout_Borda = models.IntegerField(initial=C.TIMEOUT_INITIAL)

    bid_room_X = models.CurrencyField(min=C.MIN_BID, max=C.MAX_BID, verbose_name="Bid for Room X")
    bid_room_Y = models.CurrencyField(min=C.MIN_BID, max=C.MAX_BID, verbose_name="Bid for Room Y")
    bid_room_Z = models.CurrencyField(min=C.MIN_BID, max=C.MAX_BID, verbose_name="Bid for Room Z")

    borda_count_room_X = models.StringField(
        choices=C.borda_choices,
        widget=widgets.RadioSelectHorizontal,
        verbose_name='Room X',
        blank=False,
        initial=1
    )

    borda_count_room_Y = models.StringField(
        choices=C.borda_choices,
        widget=widgets.RadioSelectHorizontal,
        verbose_name='Room Y',
        blank=False,
        initial=2
    )

    borda_count_room_Z = models.StringField(
        choices=C.borda_choices,
        widget=widgets.RadioSelectHorizontal,
        verbose_name='Room Z',
        blank=False,
        initial=3
    )

    ttc_room_X = models.StringField(
        choices=C.ttc_choices,
        widget=widgets.RadioSelectHorizontal,
        verbose_name='Room X',
        blank=False,
        initial=1
    )

    ttc_room_Y = models.StringField(
        choices=C.ttc_choices,
        widget=widgets.RadioSelectHorizontal,
        verbose_name='Room Y',
        blank=False,
        initial=2
    )
    
    ttc_room_Z = models.StringField(
        choices=C.ttc_choices,
        widget=widgets.RadioSelectHorizontal,
        verbose_name='Room Z',
        blank=False,
        initial=3
    )


    assigned_room = models.StringField() 
    assigned_room_rank = models.IntegerField()
    points = models.FloatField()  
    payment_vcg = models.CurrencyField() 
    pivotal = models.BooleanField(initial=False)  
    subtracted_points_vcg = models.FloatField() 
    payoff_points = models.FloatField()
    treatment = models.StringField()


    satisfaction = likert_field('Satisfaction', C.SATISFACTION_VN)
    dissatisfaction = likert_field('Dissatisfaction', C.DISSATISFACTION_VN)
    agreement = likert_field('Agreement', C.AGREEMENT_VN)
    appropriateness = likert_field('Appropriateness', C.APPROPRIATENESS_VN)
    fairness = likert_field('Fairness', C.FAIRNESS_VN)
    understanding = likert_field('Understanding', C.UNDERSTANDING_VN)

    benevolence = likert_field('Benevolence', C.BENEVOLENCE_VN)
    competence = likert_field('Competence', C.COMPETENCY_VN)
    integrity = likert_field('Integrity', C.INTEGRITY_VN)

    number_of_tries = models.IntegerField(initial=0)

    vcg_comprehension_1 = models.StringField(
        choices=[
            [1,
             'The app takes into account all the bids, and matches tenants to rooms in such a way that the sum of all their bids is maximised.'],
            [2,
             'The app takes into account all the bids, and matches tenants to rooms in such a way that the sum of all their bids is minimised.'],
            [3, 'The app randomly matches tenants to rooms.'],
            [4, 'The app matches tenants to rooms based on the highest individual bid.'],
        ],
        widget=widgets.RadioSelect,
        verbose_name='How does the app match tenants to rooms?',
        blank=False
    )

    vcg_comprehension_2 = models.StringField(
        choices=[
            [1,
             'Decisive influence means that if a tenant had not participated in the bidding, other tenants would have been matched to rooms they like more. '],
            [2,
             'Decisive influence means that a tenant is not interested in any of the rooms.'],
            [3,
             'Decisive influence means that a tenant is interested in all of the rooms equally.'],
            [4,
             'Decisive influence means that a tenant\'s bid determines the final matching of a room.']
        ],
        widget=widgets.RadioSelect,
        verbose_name='What does it mean for a tenant to have a decisive influence on the final matching?',
        blank=False
    )

    borda_comprehension_1 = models.StringField(
        choices=[
            [1, "No. It is possible for a tenant to get a room they assigned the least number of points to."],
            [2, "Yes, the app ensures no tenant ever gets the room they assigned the least number of points to."],
            [3, "It depends on the specific points assigned to rooms by the tenants."],
            [4, "The app does not account for the room that a tenants assigns the least number of points to."]
        ],
        widget=widgets.RadioSelect,
        verbose_name='Does the matching app guarantee that each tenant will never be matched to a room they assigned the least number of points to?',
        blank=False
    )

    borda_comprehension_2 = models.StringField(
        choices=[
            [1, "The app performs a random match."],
            [2, "The tenant who submitted their points first is matched to the room."],
            [3, "The room is matched to the tenant with the next highest points for this room."],
            [4, "The tenants who tied must re-rank their choices."]
        ],
        widget=widgets.RadioSelect,
        verbose_name='In case of a tie for the room with most points, how is the tenant who will be matched to it decided among those who assigned it the most points?',
        blank=False
    )

    ttc_comprehension_1 = models.StringField(
        choices=[
            [1,
             'For each room, the app notes which tenants liked it most, and matches tenants to rooms based on that.'],
            [2,
             'The app notes the order in which the rankings were submitted, and matches tenants to rooms based on this order.'],
            [3, 'The app notes the tenants\' last choice, and matches tenants to rooms based on that.'],
            [4, 'The app notes the tenants\' group numbers only, and matches tenants to rooms based on that.'],
        ],
        widget=widgets.RadioSelectHorizontal,
        verbose_name='What does the app note when matching tenants to rooms?',
        blank=False
    )

    ttc_comprehension_2 = models.StringField(
        choices=[
            [1, 'The app performs a random match based on the tenant number assigned to them.'],
            [2, 'The tenant who was assigned the lowest tenant number is matched to the room.'],
            [3, 'The tenant who ranked the room as the second choice is matched to the room.'],
            [4, 'The tenant who submitted their rankings first gets the room.'],
        ],
        widget=widgets.RadioSelect,
        verbose_name='If more than one tenant liked a room best, how is the tenant who will be matched to it decided among those who liked it best?',
        blank=False
    )


    def get_sorted_bids(self):
        return sorted(
            [('X', self.bid_room_X), ('Y', self.bid_room_Y), ('Z', self.bid_room_Z)],
            key=lambda x: x[1], reverse=True
        )
    
    def get_favorite_room(self, unassigned_rooms):
        rankings = {
            'X': self.field_maybe_none('ttc_room_X'),
            'Y': self.field_maybe_none('ttc_room_Y'),
            'Z': self.field_maybe_none('ttc_room_Z'),
        }
        ranked_rooms = sorted(rankings.items(), key=lambda item: item[1])

        # Return the highest ranked unassigned room
        for room, rank in ranked_rooms:
            if room in unassigned_rooms:
                return room

class Subsession(BaseSubsession):

    def creating_session(self):
        treatment_orderings = cycle(permutations(C.TREATEMENTS))
        
        if self.round_number == 1:
            for group in self.get_groups():
                treatment_order = next(treatment_orderings)
                group.treatment_order = ','.join(treatment_order)
                
                for p in group.get_players():
                    round_numbers = list(range(1, C.NUM_ROUNDS + 1))
                    treatment_order = dict(zip(treatment_order, round_numbers))
                    
                    p.participant.TREATEMENT_ORDER = treatment_order

                    for round_number, treatment in enumerate(treatment_order, start=1):
                        p.participant.vars[f'treatment_round_{round_number}'] = treatment
                        p.treatment = treatment
                    
