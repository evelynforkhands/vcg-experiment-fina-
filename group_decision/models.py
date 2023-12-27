from itertools import permutations, cycle
import itertools
from otree.api import (
    models, BaseGroup, BasePlayer, BaseSubsession, BaseConstants, widgets
)
from .helpers import get_strings

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

import itertools

class Group(BaseGroup):
    def vcg_allocation(self):
        # Helper functions
        def total_bid_for_allocation(allocation):
            return sum(bids[player.id_in_group][room] for player, room in zip(self.get_players(), allocation))

        def assign_points(player, assigned_room):
            room_bids = [('X', player.bid_room_X), ('Y', player.bid_room_Y), ('Z', player.bid_room_Z)]
            sorted_bids = sorted(room_bids, key=lambda x: x[1], reverse=True)
            tie_ranks = [rank for rank, (room, bid) in enumerate(sorted_bids) if bid == bids[player.id_in_group][assigned_room]]
            player.points_vcg = sum(points_scale[rank] for rank in tie_ranks) // len(tie_ranks)

        def calculate_payment(player, optimal_without_player):
            payment = max_total_without_player - (max_total - bids[player.id_in_group][player.assigned_room_vcg])
            pivotal = any(own != without for own, without in zip(optimal_allocation, optimal_without_player))
            return (payment if pivotal else 0, pivotal)

        # Initialize variables
        players = self.get_players()
        rooms = ['X', 'Y', 'Z']
        points_scale = {0: 100, 1: 80, 2: 60}
        bids = {player.id_in_group: {room: getattr(player, f'bid_room_{room}') for room in rooms} for player in players}

        # Determine optimal allocation
        max_total, optimal_allocation = max(
            (total_bid_for_allocation(allocation), allocation)
            for allocation in itertools.permutations(rooms)
        )

        # Assign rooms and calculate points
        for player, room in zip(players, optimal_allocation):
            player.assigned_room_vcg = room
            assign_points(player, room)

        # Calculate payments and pivotal status
        for player in players:
            # Determine optimal allocation without the current player
            max_total_without_player, optimal_without_player = max(
                (total_bid_for_allocation(allocation), allocation)
                for allocation in itertools.permutations(rooms) if player.id_in_group not in allocation
            )

            player.payment_vcg, player.pivotal = calculate_payment(player, optimal_without_player)
            player.subtracted_points_vcg = float(player.payment_vcg)
            player.points_vcg -= player.subtracted_points_vcg
            player.payoff_vcg = player.points_vcg * C.POINTS_TO_EUR


class Player(BasePlayer):
    
    start_time_VCG = models.IntegerField(initial=C.STARTTIME_INITIAL)
    start_time_TTC = models.IntegerField(initial=C.STARTTIME_INITIAL)
    start_time_Borda = models.IntegerField(initial=C.STARTTIME_INITIAL)

    timeout_VCG = models.IntegerField(initial=C.TIMEOUT_INITIAL)
    timeout_TTC = models.IntegerField(initial=C.TIMEOUT_INITIAL)
    timeout_Borda = models.IntegerField(initial=C.TIMEOUT_INITIAL)

    bid_room_X = models.CurrencyField(min=C.MIN_BID, max=C.MAX_BID, verbose_name="Bid for Room X")
    bid_room_Y = models.CurrencyField(min=C.MIN_BID, max=C.MAX_BID, verbose_name="Bid for Room Y")
    bid_room_Z = models.CurrencyField(min=C.MIN_BID, max=C.MAX_BID, verbose_name="Bid for Room Z")

    assigned_room_vcg = models.StringField() 
    points_vcg = models.FloatField()  
    payment_vcg = models.CurrencyField() 
    pivotal = models.BooleanField()  
    subtracted_points_vcg = models.FloatField() 
    payoff_vcg = models.CurrencyField() 

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
