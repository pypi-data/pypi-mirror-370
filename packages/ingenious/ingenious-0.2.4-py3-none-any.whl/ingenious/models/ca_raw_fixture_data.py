import json
import os
import sys
from collections import defaultdict
from enum import Enum
from typing import Any, List, Optional

import yaml
from pydantic import BaseModel

import ingenious.dependencies as ig_dependencies
import ingenious.utils.model_utils as model_utils
from ingenious.files.files_repository import FileStorage
from ingenious.utils.stage_executor import ProgressConsoleWrapper

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
print("parent_dir", parent_dir)
sys.path.append(parent_dir)


class RootModel_Fixturetitle(BaseModel):
    FixtureName: Optional[Any] = None
    Score: Optional[Any] = None


class RootModel_Fixture_Competition(BaseModel):
    Id: Optional[Any] = None
    Name: Optional[Any] = None
    Url: Optional[Any] = None
    ImageUrl: Optional[Any] = None
    BannerImageUrl: Optional[Any] = None
    DrinksNotificationEnabled: Optional[Any] = None
    Order: Optional[Any] = None
    TwitterHandle: Optional[Any] = None
    StartDateTime: Optional[Any] = None
    EndDateTime: Optional[Any] = None
    ThemeUrl: Optional[Any] = None
    ViewerVerdict: Optional[Any] = None
    Priority: Optional[Any] = None
    StatisticsProvider: Optional[Any] = None
    RelatedSeriesIds: Optional[Any] = None
    InteractId: Optional[Any] = None
    InteractSeasonId: Optional[Any] = None
    InteractHostId: Optional[Any] = None
    IsWomensCompetition: Optional[Any] = None
    Tour: Optional[Any] = None
    Teams: Optional[Any] = None
    Formats: Optional[Any] = None
    GameType: Optional[Any] = None
    LegacyCompetitionId: Optional[Any] = None
    IsPublished: Optional[Any] = None
    SitecoreId: Optional[Any] = None
    HasStanding: Optional[Any] = None
    UpdateFeedId: Optional[Any] = None
    SeriesGradient: Optional[Any] = None
    AssociatedMatchType: Optional[Any] = None
    OptaId: Optional[Any] = None


class RootModel_Fixture_Hometeam(BaseModel):
    Id: Optional[Any] = None
    Name: Optional[Any] = None
    NameOverride: Optional[Any] = None
    ShortName: Optional[Any] = None
    TeamColor: Optional[Any] = None
    LogoUrl: Optional[Any] = None
    BackgroundImageUrl: Optional[Any] = None
    TeambadgeImageUrl: Optional[Any] = None
    IsHomeTeam: Optional[Any] = None
    IsTossWinner: Optional[Any] = None
    IsMatchWinner: Optional[Any] = None
    BattingBonus: Optional[Any] = None
    BowlingBonus: Optional[Any] = None
    Points: Optional[Any] = None
    IsActive: Optional[Any] = None
    LegacyTeamId: Optional[Any] = None
    FixtureId: Optional[Any] = None
    UpdateFeedId: Optional[Any] = None
    IsWomensTeam: Optional[Any] = None
    WebsiteUrl: Optional[Any] = None
    Stories: Optional[Any] = None


class RootModel_Fixture_Awayteam(BaseModel):
    Id: Optional[Any] = None
    Name: Optional[Any] = None
    NameOverride: Optional[Any] = None
    ShortName: Optional[Any] = None
    TeamColor: Optional[Any] = None
    LogoUrl: Optional[Any] = None
    BackgroundImageUrl: Optional[Any] = None
    TeambadgeImageUrl: Optional[Any] = None
    IsHomeTeam: Optional[Any] = None
    IsTossWinner: Optional[Any] = None
    IsMatchWinner: Optional[Any] = None
    BattingBonus: Optional[Any] = None
    BowlingBonus: Optional[Any] = None
    Points: Optional[Any] = None
    IsActive: Optional[Any] = None
    LegacyTeamId: Optional[Any] = None
    FixtureId: Optional[Any] = None
    UpdateFeedId: Optional[Any] = None
    IsWomensTeam: Optional[Any] = None
    WebsiteUrl: Optional[Any] = None
    Stories: Optional[Any] = None


class RootModel_Fixture_Venue(BaseModel):
    Id: Optional[Any] = None
    Name: Optional[Any] = None
    City: Optional[Any] = None
    ImageUrl: Optional[Any] = None
    Latitude: Optional[Any] = None
    Longitude: Optional[Any] = None
    PhoneNumber: Optional[Any] = None
    Country: Optional[Any] = None
    VenueBay: Optional[Any] = None
    UpdateFeedId: Optional[Any] = None
    CountryName: Optional[Any] = None
    Location: Optional[Any] = None
    State: Optional[Any] = None


class RootModel_Fixture_Officials(BaseModel):
    FirstName: Optional[Any] = None
    LastName: Optional[Any] = None
    Initials: Optional[Any] = None
    UmpireType: Optional[Any] = None
    HasRetired: Optional[Any] = None


class RootModel_Players_Careerstats(BaseModel):
    PlayerId: Optional[Any] = None
    GameTypeId: Optional[Any] = None
    CompetitionId: Optional[Any] = None
    LegacyCompetitionId: Optional[Any] = None
    FixtureId: Optional[Any] = None
    TeamId: Optional[Any] = None
    BallsBowled: Optional[Any] = None
    BallsFaced: Optional[Any] = None
    BattingAverage: Optional[Any] = None
    BowlingAverage: Optional[Any] = None
    Catches: Optional[Any] = None
    Dots: Optional[Any] = None
    EconomyRate: Optional[Any] = None
    FiftiesScored: Optional[Any] = None
    FiveWickets: Optional[Any] = None
    FoursScored: Optional[Any] = None
    Games: Optional[Any] = None
    HighestRuns: Optional[Any] = None
    HundredScored: Optional[Any] = None
    InningsBatted: Optional[Any] = None
    InningsBowled: Optional[Any] = None
    MaidensBowled: Optional[Any] = None
    MinutesBatted: Optional[Any] = None
    NotOut: Optional[Any] = None
    OversBowled: Optional[Any] = None
    RunsConceded: Optional[Any] = None
    RunsScored: Optional[Any] = None
    SixesScored: Optional[Any] = None
    StrikeRate: Optional[Any] = None
    Stumpings: Optional[Any] = None
    TenWickets: Optional[Any] = None
    WicketsTaken: Optional[Any] = None
    BestBowling: Optional[Any] = None
    BestWicketsTaken: Optional[Any] = None
    BestWicketsTakenRuns: Optional[Any] = None
    HighestRunsFixtureId: Optional[Any] = None
    HighestRunsNotOut: Optional[Any] = None
    BestWicketsTakenFixtureId: Optional[Any] = None
    TotalBallsBowled: Optional[Any] = None
    TotalOversBowled: Optional[Any] = None
    BowlingStrikeRate: Optional[Any] = None
    PlayerOfTheMatch: Optional[Any] = None
    PlayerOfTheSeries: Optional[Any] = None
    EconRatePerHundred: Optional[Any] = None
    BestWicketsTakenRunsAverage: Optional[Any] = None


class RootModel_Players_Careerstats_Bowlers(BaseModel):
    TeamName: Optional[str] = None
    PlayerName: Optional[Any] = None
    BowlingAverage: Optional[Any] = None
    BowlingStrikeRate: Optional[Any] = None
    EconomyRate: Optional[Any] = None
    BestBowlingFigures: Optional[Any] = None
    FiveWicketHauls: Optional[Any] = None
    InningsBowled: Optional[Any] = None
    OversBowled: Optional[Any] = None
    TotalBallsBowled: Optional[Any] = None
    RunsConceded: Optional[Any] = None
    WicketsTaken: Optional[Any] = None
    MaidensBowled: Optional[Any] = None
    Games: Optional[Any] = None

    def __init__(
        self, careerstats: RootModel_Players_Careerstats, RootModelInstance: Any
    ) -> None:
        super().__init__(**careerstats.__dict__)
        player = RootModelInstance.Get_Player_By_Id(player_id=careerstats.PlayerId)
        self.PlayerName = player.DisplayName
        self.TeamName = player.TeamName
        self.BowlingStrikeRate = (
            self.TotalBallsBowled / self.WicketsTaken
            if self.WicketsTaken and self.TotalBallsBowled and self.WicketsTaken > 0
            else 0
        )


class RootModel_Players_Careerstats_Batsmen(BaseModel):
    TeamName: Optional[str] = None
    PlayerName: Optional[Any] = None
    BattingAverage: Optional[Any] = None
    StrikeRate: Optional[Any] = None
    HighestRuns: Optional[Any] = None
    HighestRunsNotOut: Optional[Any] = None
    InningsBatted: Optional[Any] = None
    MinutesBatted: Optional[Any] = None
    BallsFaced: Optional[Any] = None
    FoursScored: Optional[Any] = None
    SixesScored: Optional[Any] = None
    FiftiesScored: Optional[Any] = None
    HundredScored: Optional[Any] = None
    Games: Optional[Any] = None

    def __init__(
        self, careerstats: RootModel_Players_Careerstats, RootModelInstance: Any
    ) -> None:
        super().__init__(**careerstats.__dict__)
        player = RootModelInstance.Get_Player_By_Id(player_id=careerstats.PlayerId)
        self.PlayerName = player.DisplayName
        self.TeamName = player.TeamName


class RootModel_Players(BaseModel):
    CareerStats: Optional[List[RootModel_Players_Careerstats]] = None
    Id: Optional[Any] = None
    TeamId: Optional[Any] = None
    LegacyPlayerId: Optional[Any] = None
    Name: Optional[Any] = None
    IsCaptain: Optional[Any] = None
    IsWicketKeeper: Optional[Any] = None
    IsTwelthMan: Optional[Any] = None
    IsManOfTheMatch: Optional[Any] = None
    IsManOfTheSeries: Optional[Any] = None
    ManOfTheMatchOrder: Optional[Any] = None
    ManOfTheSeriesOrder: Optional[Any] = None
    Order: Optional[Any] = None
    TeamPlayerImageUrl: Optional[Any] = None
    FirstName: Optional[Any] = None
    LastName: Optional[Any] = None
    MiddleName: Optional[Any] = None
    Initials: Optional[Any] = None
    DisplayName: Optional[Any] = None
    Type: Optional[Any] = None
    BattingHandId: Optional[Any] = None
    BowlingHandId: Optional[Any] = None
    BowlingTypeId: Optional[Any] = None
    BattingHand: Optional[Any] = None
    BowlingHand: Optional[Any] = None
    BowlingType: Optional[Any] = None
    DOB: Optional[Any] = None
    BirthPlace: Optional[Any] = None
    ImageUrl: Optional[Any] = None
    Height: Optional[Any] = None
    DidyouKnow: Optional[Any] = None
    Bio: Optional[Any] = None
    Nationality: Optional[Any] = None
    LocalClub: Optional[Any] = None
    InstagramUrl: Optional[Any] = None
    TwitterUrl: Optional[Any] = None
    TiktokUrl: Optional[Any] = None
    SnapChatUrl: Optional[Any] = None
    Gender: Optional[Any] = None
    BBLShirtNumber: Optional[Any] = None
    ShirtNumber: Optional[Any] = None
    PlayerDetails: Optional[Any] = None
    FunFacts: Optional[Any] = None
    Teams: Optional[Any] = None
    IsActive: Optional[Any] = None
    SitecoreShortGUID: Optional[Any] = None
    UpdateFeedId: Optional[Any] = None
    VideoId: Optional[Any] = None
    Stories: Optional[Any] = None
    DisplayeNameOverride: Optional[Any] = None


class RootModel_Players_Curated(BaseModel):
    # Provided a curated player object
    TeamName: Optional[str] = None
    DisplayName: Optional[Any] = None
    IsCaptain: Optional[Any] = None
    IsWicketKeeper: Optional[Any] = None
    IsTwelthMan: Optional[Any] = None
    Order: Optional[Any] = None
    Type: Optional[Any] = None
    BattingHandId: Optional[Any] = None
    BowlingHandId: Optional[Any] = None
    BowlingTypeId: Optional[Any] = None
    BattingHand: Optional[Any] = None
    BowlingHand: Optional[Any] = None
    BowlingType: Optional[Any] = None
    DOB: Optional[Any] = None
    BirthPlace: Optional[Any] = None
    Height: Optional[Any] = None
    DidyouKnow: Optional[Any] = None
    Bio: Optional[Any] = None
    Nationality: Optional[Any] = None
    FunFacts: Optional[Any] = None
    IsActive: Optional[Any] = None

    def __init__(self, player: RootModel_Players, RootModelInstance: Any) -> None:
        super().__init__(**player.__dict__)
        self.TeamName = RootModelInstance.Get_Team_By_Id(team_id=player.TeamId).Name


class RootModel_Innings_Batsmen(BaseModel):
    PlayerId: Optional[Any] = None
    BallsFaced: Optional[Any] = None
    BowledByPlayerId: Optional[Any] = None
    DismissalTypeId: Optional[Any] = None
    DismissedByPlayerId: Optional[Any] = None
    DismissalText: Optional[Any] = None
    DismissalBall: Optional[Any] = None
    BattingStartDay: Optional[Any] = None
    FoursScored: Optional[Any] = None
    SixesScored: Optional[Any] = None
    RunsScored: Optional[Any] = None
    BattingMinutes: Optional[Any] = None
    IsOnStrike: Optional[Any] = None
    IsBatting: Optional[Any] = None
    BattingOrder: Optional[Any] = None
    IsOut: Optional[Any] = None
    StrikeRate: Optional[Any] = None
    Videos: Optional[Any] = None


class RootModel_Innings_Bowlers(BaseModel):
    PlayerId: Optional[Any] = None
    OversBowled: Optional[Any] = None
    MaidensBowled: Optional[Any] = None
    BallsBowled: Optional[Any] = None
    TotalBallsBowled: Optional[Any] = None
    DotBalls: Optional[Any] = None
    NoBalls: Optional[Any] = None
    WideBalls: Optional[Any] = None
    Order: Optional[Any] = None
    RunsConceded: Optional[Any] = None
    WicketsTaken: Optional[Any] = None
    IsOnStrike: Optional[Any] = None
    IsNonStrike: Optional[Any] = None
    Economy: Optional[Any] = None
    Videos: Optional[Any] = None


class RootModel_Innings_Bowlers_Extended(BaseModel):
    TeamName: Optional[str] = None
    PlayerName: Optional[str] = None
    PlayerId: Optional[Any] = None
    BowlingAverage: Optional[Any] = None
    EconomyRate: Optional[Any] = None
    StrikeRate: Optional[Any] = None
    OversBowled: Optional[Any] = None
    MaidensBowled: Optional[Any] = None
    BallsBowled: Optional[Any] = None
    TotalBallsBowled: Optional[Any] = None
    DotBalls: Optional[Any] = None
    NoBalls: Optional[Any] = None
    WideBalls: Optional[Any] = None
    Order: Optional[Any] = None
    RunsConceded: Optional[Any] = None
    WicketsTaken: Optional[Any] = None
    IsOnStrike: Optional[Any] = None
    IsNonStrike: Optional[Any] = None
    Economy: Optional[Any] = None

    def __init__(
        self, bowler: RootModel_Innings_Bowlers, RootModelInstance: Any
    ) -> None:
        # Add the player name and team name to the bowler object
        super().__init__(**bowler.__dict__)
        player: RootModel_Players_Curated = RootModelInstance.Get_Player_By_Id(
            player_id=self.PlayerId
        )
        self.PlayerName = player.DisplayName
        self.TeamName = player.TeamName
        self.BowlingAverage = (
            self.RunsConceded / self.WicketsTaken
            if self.RunsConceded and self.WicketsTaken and self.WicketsTaken > 0
            else 0
        )
        self.EconomyRate = self.Economy
        self.StrikeRate = (
            self.TotalBallsBowled / self.WicketsTaken
            if self.TotalBallsBowled and self.WicketsTaken and self.WicketsTaken > 0
            else 0
        )


class RootModel_Innings_Batsmen_Extended(BaseModel):
    TeamName: Optional[str] = None
    PlayerName: Optional[str] = None
    PlayerId: Optional[Any] = None
    BallsFaced: Optional[Any] = None
    BowledByPlayerId: Optional[Any] = None
    DismissalTypeId: Optional[Any] = None
    DismissedByPlayerId: Optional[Any] = None
    DismissalText: Optional[Any] = None
    DismissalBall: Optional[Any] = None
    BattingStartDay: Optional[Any] = None
    FoursScored: Optional[Any] = None
    SixesScored: Optional[Any] = None
    RunsScored: Optional[Any] = None
    BattingMinutes: Optional[Any] = None
    IsOnStrike: Optional[Any] = None
    IsBatting: Optional[Any] = None
    BattingOrder: Optional[Any] = None
    IsOut: Optional[Any] = None
    StrikeRate: Optional[Any] = None

    def __init__(
        self, batsman: RootModel_Innings_Batsmen, RootModelInstance: Any
    ) -> None:
        # Add the player name and team name to the batsman object
        super().__init__(**batsman.__dict__)
        player: RootModel_Players_Curated = RootModelInstance.Get_Player_By_Id(
            player_id=self.PlayerId
        )
        self.PlayerName = player.DisplayName
        self.TeamName = player.TeamName


class RootModel_Innings_Overs_Balls_Comments(BaseModel):
    Id: Optional[Any] = None
    CommentTypeId: Optional[Any] = None
    CommentType: Optional[Any] = None
    Video: Optional[Any] = None
    InningBallId: Optional[Any] = None
    Message: Optional[Any] = None
    OverNumber: Optional[Any] = None
    Order: Optional[Any] = None


class RootModel_Innings_Overs_Balls(BaseModel):
    Id: Optional[Any] = None
    InningOverId: Optional[Any] = None
    BallDateTime: Optional[Any] = None
    BallNumber: Optional[Any] = None
    TotalBallNumber: Optional[Any] = None
    IsWicket: Optional[Any] = None
    DismissalTypeId: Optional[Any] = None
    DismissalPlayerId: Optional[Any] = None
    BowlerPlayerId: Optional[Any] = None
    BattingPlayerId: Optional[Any] = None
    NonStrikeBattingPlayerId: Optional[Any] = None
    ShotAngle: Optional[Any] = None
    ShotMagnitude: Optional[Any] = None
    BattingHandId: Optional[Any] = None
    BattingHand: Optional[Any] = None
    FieldingPosition: Optional[Any] = None
    RunsConceded: Optional[Any] = None
    Extras: Optional[Any] = None
    Runs: Optional[Any] = None
    RunsScored: Optional[Any] = None
    Comments: Optional[List[RootModel_Innings_Overs_Balls_Comments]] = None
    LengthTypeId: Optional[Any] = None
    LengthType: Optional[Any] = None
    LineTypeId: Optional[Any] = None
    LineType: Optional[Any] = None
    AppealDismissalTypeId: Optional[Any] = None
    AppealDismissalType: Optional[Any] = None
    BattingConnectionId: Optional[Any] = None
    BattingConnection: Optional[Any] = None
    BattingFeetId: Optional[Any] = None
    BattingFeet: Optional[Any] = None
    BattingShotTypeId: Optional[Any] = None
    BattingShotType: Optional[Any] = None
    BowlingDetailId: Optional[Any] = None
    BowlingDetail: Optional[Any] = None
    BowlingFromId: Optional[Any] = None
    BowlingFrom: Optional[Any] = None
    BowlingTypeId: Optional[Any] = None
    BowlingType: Optional[Any] = None
    BowlingHandId: Optional[Any] = None
    BowlingHand: Optional[Any] = None
    OutcomeId: Optional[Any] = None
    Outcome: Optional[Any] = None
    ReferralOutcomeId: Optional[Any] = None
    ReferralOutcome: Optional[Any] = None
    NoBallReasonId: Optional[Any] = None
    NoBallReason: Optional[Any] = None
    Position: Optional[Any] = None
    IsWide: Optional[Any] = None
    IsNoBall: Optional[Any] = None
    IsByes: Optional[Any] = None
    IsLegByes: Optional[Any] = None
    IsAirControlled: Optional[Any] = None
    IsAppeal: Optional[Any] = None
    DecisionOfficialId: Optional[Any] = None
    IsFreeHit: Optional[Any] = None
    IsNewBall: Optional[Any] = None
    IsPowerPlay: Optional[Any] = None
    IsBattingPowerPlay: Optional[Any] = None
    IsFloodLit: Optional[Any] = None
    IsReferred: Optional[Any] = None
    TeamRuns: Optional[Any] = None
    RunsByes: Optional[Any] = None
    RunsWide: Optional[Any] = None
    RunsLegByes: Optional[Any] = None
    NoBallsCount: Optional[Any] = None
    IsBoundry: Optional[Any] = None
    IsAirNotControlled: Optional[Any] = None
    CatchDifficulty: Optional[Any] = None


class RootModel_Innings_Overs_Balls_Flat(BaseModel):
    InningsNumber: Optional[Any] = None
    BattingTeam: Optional[Any] = None
    BowlingTeam: Optional[Any] = None
    OverNumber: Optional[Any] = None
    Id: Optional[Any] = None
    InningOverId: Optional[Any] = None
    BallDateTime: Optional[Any] = None
    BallNumber: Optional[Any] = None
    TotalBallNumber: Optional[Any] = None
    IsWicket: Optional[Any] = None
    DismissalTypeId: Optional[Any] = None
    DismissalPlayerId: Optional[Any] = None
    BowlerPlayerId: Optional[Any] = None
    BattingPlayerId: Optional[Any] = None
    NonStrikeBattingPlayerId: Optional[Any] = None
    ShotAngle: Optional[Any] = None
    ShotMagnitude: Optional[Any] = None
    BattingHandId: Optional[Any] = None
    BattingHand: Optional[Any] = None
    FieldingPosition: Optional[Any] = None
    RunsConceded: Optional[Any] = None
    Extras: Optional[Any] = None
    Runs: Optional[Any] = None
    RunsScored: Optional[Any] = None
    Comments: Optional[str] = None
    LengthTypeId: Optional[Any] = None
    LengthType: Optional[Any] = None
    LineTypeId: Optional[Any] = None
    LineType: Optional[Any] = None
    AppealDismissalTypeId: Optional[Any] = None
    AppealDismissalType: Optional[Any] = None
    BattingConnectionId: Optional[Any] = None
    BattingConnection: Optional[Any] = None
    BattingFeetId: Optional[Any] = None
    BattingFeet: Optional[Any] = None
    BattingShotTypeId: Optional[Any] = None
    BattingShotType: Optional[Any] = None
    BowlingDetailId: Optional[Any] = None
    BowlingDetail: Optional[Any] = None
    BowlingFromId: Optional[Any] = None
    BowlingFrom: Optional[Any] = None
    BowlingTypeId: Optional[Any] = None
    BowlingType: Optional[Any] = None
    BowlingHandId: Optional[Any] = None
    BowlingHand: Optional[Any] = None
    OutcomeId: Optional[Any] = None
    Outcome: Optional[Any] = None
    ReferralOutcomeId: Optional[Any] = None
    ReferralOutcome: Optional[Any] = None
    NoBallReasonId: Optional[Any] = None
    NoBallReason: Optional[Any] = None
    Position: Optional[Any] = None
    IsWide: Optional[Any] = None
    IsNoBall: Optional[Any] = None
    IsByes: Optional[Any] = None
    IsLegByes: Optional[Any] = None
    IsAirControlled: Optional[Any] = None
    IsAppeal: Optional[Any] = None
    DecisionOfficialId: Optional[Any] = None
    IsFreeHit: Optional[Any] = None
    IsNewBall: Optional[Any] = None
    IsPowerPlay: Optional[Any] = None
    IsBattingPowerPlay: Optional[Any] = None
    IsFloodLit: Optional[Any] = None
    IsReferred: Optional[Any] = None
    TeamRuns: Optional[Any] = None
    RunsByes: Optional[Any] = None
    RunsWide: Optional[Any] = None
    RunsLegByes: Optional[Any] = None
    NoBallsCount: Optional[Any] = None
    IsBoundry: Optional[Any] = None
    IsAirNotControlled: Optional[Any] = None
    CatchDifficulty: Optional[Any] = None


class RootModel_Innings_Overs(BaseModel):
    Id: Optional[Any] = None
    OverNumber: Optional[Any] = None
    Runrate: Optional[Any] = None
    RunsConceded: Optional[Any] = None
    Wickets: Optional[Any] = None
    RunsExtras: Optional[Any] = None
    TotalInningRuns: Optional[Any] = None
    TotalInningWickets: Optional[Any] = None
    TotalRuns: Optional[Any] = None
    Balls: Optional[List[RootModel_Innings_Overs_Balls]] = None


class RootModel_Innings_Overs_Extended(RootModel_Innings_Overs):
    InningsNumber: Optional[Any] = None
    BattingTeam: Optional[Any] = None


class RootModel_Innings(BaseModel):
    Id: Optional[Any] = None
    FixtureId: Optional[Any] = None
    InningNumber: Optional[Any] = None
    BattingTeamId: Optional[Any] = None
    Batsmen: Optional[List[RootModel_Innings_Batsmen]] = None
    BowlingTeamId: Optional[Any] = None
    Bowlers: Optional[List[RootModel_Innings_Bowlers]] = None
    Wickets: Optional[Any] = None
    Overs: Optional[List[RootModel_Innings_Overs]] = None
    IsDeclared: Optional[Any] = None
    IsFollowOn: Optional[Any] = None
    IsForfeited: Optional[Any] = None
    OvernightRuns: Optional[Any] = None
    OvernightWickets: Optional[Any] = None
    ByesRuns: Optional[Any] = None
    LegByesRuns: Optional[Any] = None
    NoBalls: Optional[Any] = None
    Penalties: Optional[Any] = None
    TotalExtras: Optional[Any] = None
    WideBalls: Optional[Any] = None
    OversBowled: Optional[Any] = None
    Balls: Optional[Any] = None
    BallsRemaining: Optional[Any] = None
    RunsScored: Optional[Any] = None
    RequiredRunRate: Optional[Any] = None
    CurrentRunRate: Optional[Any] = None
    NumberOfWicketsFallen: Optional[Any] = None
    Day: Optional[Any] = None
    DuckworthLewisOvers: Optional[Any] = None
    DuckworthLewisTarget: Optional[Any] = None
    Partnership: Optional[Any] = None
    RunStats: Optional[Any] = None
    TotalRuns: Optional[Any] = None
    TotalBallsBowled: Optional[Any] = None

    def Get_Overs(self) -> List[Any]:
        overs: List[RootModel_Innings_Overs_Extended] = list()
        for over in self.Overs or []:
            if over is not None:
                over_extended = RootModel_Innings_Overs_Extended.model_validate(
                    over.__dict__
                )
                over_extended.InningsNumber = self.InningNumber
                over_extended.BattingTeam = self.BattingTeamId
                overs.append(over_extended)
        return overs


class RootModel_Teamform_Fixtures_Opponentteam(BaseModel):
    TeamId: Optional[Any] = None
    Name: Optional[Any] = None
    LogoUrl: Optional[Any] = None
    ShortName: Optional[Any] = None


class RootModel_Headtohead_Fixtures_Opponentteam(BaseModel):
    TeamId: Optional[Any] = None
    Name: Optional[Any] = None
    LogoUrl: Optional[Any] = None
    ShortName: Optional[Any] = None


class RootModel_Teamform_Fixtures(BaseModel):
    FixtureId: Optional[Any] = None
    ResultText: Optional[Any] = None
    IsWon: Optional[Any] = None
    Result: Optional[Any] = None
    StartDateTime: Optional[Any] = None
    EndDateTime: Optional[Any] = None
    OpponentTeam: Optional[RootModel_Teamform_Fixtures_Opponentteam] = None


class RootModel_Headtohead_Fixtures(BaseModel):
    FixtureId: Optional[Any] = None
    ResultText: Optional[Any] = None
    IsWon: Optional[Any] = None
    Result: Optional[Any] = None
    StartDateTime: Optional[Any] = None
    EndDateTime: Optional[Any] = None
    OpponentTeam: Optional[RootModel_Headtohead_Fixtures_Opponentteam] = None


class RootModel_Teamform(BaseModel):
    Fixtures: Optional[List[RootModel_Teamform_Fixtures]] = None
    TeamId: Optional[Any] = None
    Name: Optional[Any] = None
    LogoUrl: Optional[Any] = None
    ShortName: Optional[Any] = None


class RootModel_Headtohead(BaseModel):
    Fixtures: Optional[List[RootModel_Headtohead_Fixtures]] = None
    TeamId: Optional[Any] = None
    Name: Optional[Any] = None
    LogoUrl: Optional[Any] = None
    ShortName: Optional[Any] = None


class RootModel_Fixture(BaseModel):
    Competition: Optional[RootModel_Fixture_Competition] = None
    HomeTeam: Optional[RootModel_Fixture_Hometeam] = None
    AwayTeam: Optional[RootModel_Fixture_Awayteam] = None
    Streams: Optional[Any] = None
    Venue: Optional[RootModel_Fixture_Venue] = None
    HasRadioStream: Optional[Any] = None
    Id: Optional[Any] = None
    Name: Optional[Any] = None
    StartDateTime: Optional[Any] = None
    EndDateTime: Optional[Any] = None
    GameTypeId: Optional[Any] = None
    GameType: Optional[Any] = None
    IsLive: Optional[Any] = None
    IsCompleted: Optional[Any] = None
    IsDuckworthLewis: Optional[Any] = None
    MatchDay: Optional[Any] = None
    NumberOfDays: Optional[Any] = None
    ResultText: Optional[Any] = None
    ResultTypeId: Optional[Any] = None
    ResultType: Optional[Any] = None
    GameStatusId: Optional[Any] = None
    GameStatus: Optional[Any] = None
    TossResult: Optional[Any] = None
    TossDecision: Optional[Any] = None
    WinningMargin: Optional[Any] = None
    WinTypeId: Optional[Any] = None
    WinType: Optional[Any] = None
    TicketUrl: Optional[Any] = None
    Featured: Optional[Any] = None
    IsWomensMatch: Optional[Any] = None
    FanHashTag: Optional[Any] = None
    TwitterHandle: Optional[Any] = None
    SocialEventId: Optional[Any] = None
    TuneIn: Optional[Any] = None
    BackgroundImageUrl: Optional[Any] = None
    MatchDayHomePageImageUrl: Optional[Any] = None
    FanSocialEventId: Optional[Any] = None
    IsVideoReplays: Optional[Any] = None
    GamedayStatus: Optional[Any] = None
    IsEnableGameday: Optional[Any] = None
    MoreInfoUrl: Optional[Any] = None
    OversRemaining: Optional[Any] = None
    Order: Optional[Any] = None
    CompetitionId: Optional[Any] = None
    Tour: Optional[Any] = None
    VenueId: Optional[Any] = None
    HomeTeamId: Optional[Any] = None
    AwayTeamId: Optional[Any] = None
    EventSchedule: Optional[Any] = None
    Channels: Optional[Any] = None
    Officials: Optional[List[RootModel_Fixture_Officials]] = None
    LegacyFixtureId: Optional[Any] = None
    IsInProgress: Optional[Any] = None
    TotalOvers: Optional[Any] = None
    TotalBalls: Optional[Any] = None
    PlayOfDayVideoId: Optional[Any] = None
    IsPublished: Optional[Any] = None
    SitecoreId: Optional[Any] = None
    UpdateFeedId: Optional[Any] = None
    Priority: Optional[Any] = None
    Days: Optional[Any] = None
    Hours: Optional[Any] = None
    LegacyCompetitionId: Optional[Any] = None
    OverrideVenueName: Optional[Any] = None
    HasLiveBlog: Optional[Any] = None
    IsBattingPowerPlay: Optional[Any] = None
    IsAIInsightsEnabled: Optional[Any] = None


class RootModel_Fixture_Extended(RootModel_Fixture):
    # Extend the base model with additional fields
    FixtureName: Optional[str] = None
    FixtureScore: Optional[str] = None


class RootModel(BaseModel):
    Fixture: Optional[RootModel_Fixture] = None
    Players: Optional[List[RootModel_Players]] = None
    FixtureTitle: Optional[RootModel_Fixturetitle] = None
    Innings: Optional[List[RootModel_Innings]] = None
    TeamForm: Optional[List[RootModel_Teamform]] = None
    HeadToHead: Optional[List[RootModel_Headtohead]] = None
    FeedTimestamp: Optional[Any] = None
    FeedId: Optional[Any] = None
    Revision: Optional[Any] = None

    # Declare private internal variables
    _NewBallsMarked: bool = False
    _NewBallsInThisFeed: Optional[List[RootModel_Innings_Overs_Balls_Flat]] = None
    _CurrentBall: Optional[RootModel_Innings_Overs_Balls_Flat] = None
    _ball_history_path = "./ball_history/"
    _ball_history_file_name = ""
    _progress: Optional[Any] = None

    def Get_Fixture_As_Yml(self) -> Any:
        if not self.Fixture:
            return "No fixture data"
        Fixture_Name = f"Fixture {self.Fixture.Id}:{self.Fixture.Name}"
        output = f"## {Fixture_Name}\n"
        output += "```yaml\n"
        output_dic = dict()
        # Add the non-complex fields to the dictionary
        output_dic.update(
            {
                field.FieldName: getattr(self.Fixture, field.FieldName)
                for field in model_utils.Get_Model_Properties(RootModel_Fixture)
                if model_utils.Is_Non_Complex_Field_Check_By_Type(field.FieldType)
            }
        )
        output_dic_filtered = {
            (
                "HomeTeamName"
                if k == "HomeTeamId"
                else "AwayTeamName"
                if k == "AwayTeamId"
                else k
            ): (
                self.Fixture.HomeTeam.Name
                if self.Fixture.HomeTeam
                else "N/A"
                if k == "HomeTeamId"
                else self.Fixture.AwayTeam.Name
                if self.Fixture.AwayTeam
                else "N/A"
                if k == "AwayTeamId"
                else v
            )
            for k, v in output_dic.items()
            if v not in (None, "", "None", [])
        }
        if self.FixtureTitle:
            output_dic_filtered["Fixture Name"] = self.FixtureTitle.FixtureName
            output_dic_filtered["Fixture Score"] = self.FixtureTitle.Score

        output += yaml.dump(output_dic_filtered, default_flow_style=False)
        output += "\n```\n"

        return output

    def Get_Player_By_Id(self, player_id: Any) -> Any:
        for player in self.Players or []:
            if player.Id == player_id:
                return RootModel_Players_Curated(player, self)

    def Get_Inning_By_Number(self, inning_number: int) -> Any:
        for inning in self.Innings or []:
            if inning.InningNumber == inning_number:
                return inning
        return None

    def Get_Batsman_By_Id(self, inning: Any, player_id: Any) -> Any:
        for batsman in inning.Batsmen:
            if batsman.PlayerId == player_id:
                return batsman
        return None

    def Get_Bowler_By_Id(self, inning: Any, player_id: Any) -> Any:
        for bowler in inning.Bowlers:
            if bowler.PlayerId == player_id:
                return bowler
        return None

    def Get_Overs_By_Number(self, inning: Any, over_number: int) -> Any:
        for over in inning.Overs:
            if over.OverNumber == over_number:
                return over
        return None

    def Get_Overs_By_Id(self, inning: Any, over_id: Any) -> Any:
        for over in inning.Overs:
            if over.Id == over_id:
                return over
        return None

    def Get_Overs_By_Bowler(self, inning: Any, bowler_id: Any) -> Any:
        for over in inning.Overs:
            if over.BowlerId == bowler_id:
                return over
        return None

    def Get_Overs_By_Batsman(self, inning: Any, batsman_id: Any) -> Any:
        for over in inning.Overs:
            if over.BatsmanId == batsman_id:
                return over
        return None

    def Get_Latest_Inning(self) -> Any:
        if not self.Innings:
            return None
        return sorted(self.Innings, key=lambda x: x.InningNumber or 0)[-1]

    def Get_Latest_Over(self) -> Any:
        inning = self.Get_Latest_Inning()
        if not inning or not inning.Overs:
            return None
        return sorted(inning.Overs, key=lambda x: x.OverNumber or 0)[-1]

    def Get_Latest_Over_Balls(self, as_csv: bool = True) -> Any:
        over = self.Get_Latest_Over()
        if not over:
            return "No over data" if as_csv else []
        if as_csv:
            over_balls = over.Balls or []
            csv_string = "## Last Over balls\n"
            csv_string += model_utils.List_To_Csv(
                obj=over_balls,
                row_header_columns=[
                    prop.FieldName
                    for prop in model_utils.Get_Model_Properties(
                        RootModel_Innings_Overs_Balls
                    )
                    if model_utils.Is_Non_Complex_Field_Check_By_Type(prop.FieldType)
                ],
                name="Over Balls",
            )
            return csv_string
        return sorted(over.Balls or [], key=lambda x: x.BallNumber or 0)

    def Get_Latest_Ball(self) -> Any:
        balls = self.Get_Latest_Over_Balls()
        return balls[-1]

    def Set_Current_Ball(self, ball: Any) -> None:
        self._CurrentBall = ball
        print("")

    def Get_Current_Ball(self, as_yml: bool = False) -> Any:
        """
        Method used to track current ball while processing new balls in the feed
        """
        if as_yml:
            ret = "## Latest Ball\n"
            ret += model_utils.Object_To_Yaml(self._CurrentBall)
        else:
            ret = self._CurrentBall

        return ret

    def Get_All_Balls_by_Player(self, as_csv: bool = True) -> Any:
        try:
            balls = self.Get_All_Balls()
            if not isinstance(balls, list):
                balls = []
        except Exception:
            balls = []

        try:
            players = {p.Id: {"Id": p.Id, "Name": p.DisplayName} for p in self.Players}
        except Exception:
            players = {}

        # Helper function to aggregate stats by a given key
        def aggregate_by_key(balls: List[Any], key: str) -> dict[str, dict[str, Any]]:
            grouped_stats = defaultdict(
                lambda: {
                    "TotalBalls": 0,
                    "TotalRunsConceded": 0,
                    "TotalRunsScored": 0,
                    "Wickets": 0,
                }
            )
            for ball in balls:
                try:
                    ball = dict(ball)
                    group = grouped_stats[ball.get(key, "Unknown")]
                    group["TotalBalls"] += 1
                    group["TotalRunsConceded"] += ball.get("RunsConceded", 0)
                    group["TotalRunsScored"] += ball.get("RunsScored", 0)
                    group["Wickets"] += 1 if ball.get("IsWicket", False) else 0
                except Exception:
                    pass
            return [{key: k, **v} for k, v in grouped_stats.items()]

        # Aggregate by BowlerPlayerId
        try:
            stats_by_bowler = aggregate_by_key(balls, "BowlerPlayerId")
            for stat in stats_by_bowler:
                stat["BowlerName"] = players.get(
                    stat.get("BowlerPlayerId", ""), {}
                ).get("Name", "Unknown")
        except Exception:
            stats_by_bowler = []

        # Aggregate by BattingPlayerId
        try:
            stats_by_batter = defaultdict(
                lambda: {"TotalBalls": 0, "TotalRunsScored": 0, "Wickets": 0}
            )
            for ball in balls:
                try:
                    ball = dict(ball)
                    key = (
                        ball.get("BattingPlayerId", "Unknown"),
                        ball.get("BowlerPlayerId", "Unknown"),
                    )
                    group = stats_by_batter[key]
                    group["TotalBalls"] += 1
                    group["TotalRunsConceded"] += ball.get("RunsConceded", 0)
                    group["TotalRunsScored"] += ball.get("RunsScored", 0)
                    group["Wickets"] += 1 if ball.get("IsWicket", False) else 0
                except Exception:
                    pass

            stats_by_batter = [
                {
                    "BattingPlayerId": k[0],
                    "BowlerPlayerId": k[1],
                    "BatterName": players.get(k[0], {}).get("Name", "Unknown"),
                    "BowlerName": players.get(k[1], {}).get("Name", "Unknown"),
                    **v,
                }
                for k, v in stats_by_batter.items()
            ]
        except Exception:
            stats_by_batter = []

        # Aggregate by both BattingPlayerId and BowlerPlayerId
        try:
            stats_by_batter_bowler = defaultdict(
                lambda: {
                    "TotalBalls": 0,
                    "TotalRunsConceded": 0,
                    "TotalRunsScored": 0,
                    "Wickets": 0,
                }
            )
            for ball in balls:
                try:
                    ball = dict(ball)
                    key = (
                        ball.get("BattingPlayerId", "Unknown"),
                        ball.get("BowlerPlayerId", "Unknown"),
                    )
                    group = stats_by_batter_bowler[key]
                    group["TotalBalls"] += 1
                    group["TotalRunsConceded"] += ball.get("RunsConceded", 0)
                    group["TotalRunsScored"] += ball.get("RunsScored", 0)
                    group["Wickets"] += 1 if ball.get("IsWicket", False) else 0
                except Exception:
                    pass

            stats_by_batter_bowler = [
                {
                    "BattingPlayerId": k[0],
                    "BowlerPlayerId": k[1],
                    "BatterName": players.get(k[0], {}).get("Name", "Unknown"),
                    "BowlerName": players.get(k[1], {}).get("Name", "Unknown"),
                    **v,
                }
                for k, v in stats_by_batter_bowler.items()
            ]
        except Exception:
            stats_by_batter_bowler = []

        # Generate CSV strings if requested
        if as_csv:
            try:
                csv_string = "## Ball stats grouped by Bowler:\n"
                csv_string += model_utils.List_To_Csv(
                    obj=stats_by_bowler,
                    row_header_columns=[
                        "BowlerPlayerId",
                        "BowlerName",
                        "TotalBalls",
                        "TotalRunsConceded",
                        "TotalRunsScored",
                        "Wickets",
                    ],
                    name="Player_Ball",
                )
                csv_string += "\n\n# Ball stats grouped by Batting:\n"
                csv_string += model_utils.List_To_Csv(
                    obj=stats_by_batter,
                    row_header_columns=[
                        "BattingPlayerId",
                        "BatterName",
                        "TotalBalls",
                        "TotalRunsConceded",
                        "TotalRunsScored",
                        "Wickets",
                    ],
                    name="Player_Ball",
                )
                csv_string += "\n\n# Ball stats grouped by Batting and Bowler:\n"
                csv_string += model_utils.List_To_Csv(
                    obj=stats_by_batter_bowler,
                    row_header_columns=[
                        "BattingPlayerId",
                        "BatterName",
                        "BowlerPlayerId",
                        "BowlerName",
                        "TotalBalls",
                        "TotalRunsConceded",
                        "TotalRunsScored",
                        "Wickets",
                    ],
                    name="Player_Ball",
                )
                return csv_string
            except Exception:
                return None
        else:
            return {
                "stats_by_bowler": stats_by_bowler,
                "stats_by_batter": stats_by_batter,
                "stats_by_batter_bowler": stats_by_batter_bowler,
            }

    def Get_All_Balls(self) -> List[RootModel_Innings_Overs_Balls_Flat]:
        balls = list()
        if self.Innings is not None:
            for inning in self.Innings:
                if inning.Overs is not None:
                    for over in inning.Overs:
                        # Add the Over Number to the Ball object
                        if over.Balls is not None:
                            for ball in over.Balls:
                                ball_flat = RootModel_Innings_Overs_Balls_Flat()
                                # Copy the values from the ball object to the flat object but skip the nested objects
                                for key, value in ball.__dict__.items():
                                    if not isinstance(value, list):
                                        setattr(ball_flat, key, value)
                                # Concatenate the comments into a single string
                                if ball.Comments is not None:
                                    comments = [
                                        comment.Message for comment in ball.Comments
                                    ]
                                    ball_flat.Comments = " ".join(comments)
                                # Now add the additional fields
                                ball_flat.InningsNumber = inning.InningNumber
                                ball_flat.BattingTeam = inning.BattingTeamId
                                ball_flat.BowlingTeam = inning.BowlingTeamId
                                ball_flat.OverNumber = over.OverNumber
                                balls.append(ball_flat)
        return balls

    async def Get_New_Balls(
        self,
        config: ig_dependencies.Config,
        progress: ProgressConsoleWrapper,
        task_id: str,
    ) -> List[RootModel_Innings_Overs_Balls_Flat]:
        if self._NewBallsMarked:
            progress.progress.print("New Balls already marked.")
            return self._NewBallsInThisFeed

        # Define the parquet file path
        self._ball_history_path = "./ball_history/"
        self._ball_history_file_name = (
            f"ball_history_for_fixture_id_{self.Fixture.Id}.json"
        )

        # Check if the parquet file already exists
        fs = FileStorage(ig_dependencies.get_config())
        file_check: bool = await fs.check_if_file_exists(
            file_path=self._ball_history_path, file_name=self._ball_history_file_name
        )

        if not file_check:
            init_val = RootModel_Innings_Overs_Balls_Flat()
            init_val.OverNumber = 0
            init_val.BallNumber = 0
            init_val.InningsNumber = 0
            contents = json.dumps(init_val.__dict__, indent=4)
            await fs.write_file(
                file_path=self._ball_history_path,
                file_name=self._ball_history_file_name,
                contents=contents,
            )
        else:
            contents = await fs.read_file(
                file_path=self._ball_history_path,
                file_name=self._ball_history_file_name,
            )
            init_val = RootModel_Innings_Overs_Balls_Flat.model_validate_json(contents)

        Last_Seen_Over = init_val.OverNumber
        Last_Seen_Ball = init_val.BallNumber
        Last_Seen_Innings = init_val.InningsNumber

        ball_data = self.Get_All_Balls()

        # Capture the number of balls in the new data
        # progress.progress.print(f"Found {len(ball_data)} balls in Feed: {self.FeedId}")

        # Find all Balls in new data where innings number is greater than the
        # last ball in the parquet file
        ball_data_filtered = [
            ball for ball in ball_data if ball.InningsNumber > Last_Seen_Innings
        ]

        # Find all balls in new data where over number is greater than the
        # last ball in the parquet file
        ball_data_filtered.extend(
            [
                ball
                for ball in ball_data
                if ball.InningsNumber == Last_Seen_Innings
                and ball.OverNumber > Last_Seen_Over
            ]
        )

        # If over number is equal to the last ball in the parquet file,
        # find all balls where ball number is greater
        ball_data_filtered.extend(
            [
                ball
                for ball in ball_data
                if ball.InningsNumber == Last_Seen_Innings
                and ball.OverNumber == Last_Seen_Over
                and ball.BallNumber > Last_Seen_Ball
            ]
        )

        # Capture Number of Balls in parquet file after removing duplicates
        progress.progress.print(
            f"Found {len(ball_data_filtered)} new balls in the data."
        )

        if len(ball_data_filtered) > 0:
            Last_Seen_Over = ball_data_filtered[0].OverNumber
            Last_Seen_Ball = ball_data_filtered[0].BallNumber
            Last_Seen_Innings = ball_data_filtered[0].InningsNumber

            # Dump the first item in ball_data to the json file
            await fs.write_file(
                file_path=self._ball_history_path,
                file_name=self._ball_history_file_name,
                contents=json.dumps(ball_data_filtered[0].__dict__, indent=4),
            )

        # Update the new balls marked flag
        self._NewBallsInThisFeed = ball_data_filtered
        self._NewBallsMarked = True
        return self._NewBallsInThisFeed

    async def Delete_New_Ball_Watermark(self, config: ig_dependencies.Config) -> None:
        fs = FileStorage(config)
        await fs.delete_file(
            file_path=self._ball_history_path, file_name=self._ball_history_file_name
        )
        self._NewBallsMarked = False
        self._NewBallsInThisFeed = None

    def Get_Batting_Team(self) -> Any:
        inning = self.Get_Latest_Inning()
        return self.Get_Team_By_Id(inning.BattingTeamId)

    def Get_Bowling_Team(self) -> Any:
        inning = self.Get_Latest_Inning()
        return self.Get_Team_By_Id(inning.BowlingTeamId)

    def Get_Inning_By_Id(self, inning_id: Any) -> Any:
        for inning in self.Innings:
            if inning.Id == inning_id:
                return inning
        return None

    def Get_Teams(self, as_csv: bool = False) -> Any:
        teams = list()
        teams.append(self.Fixture.HomeTeam)
        teams.append(self.Fixture.AwayTeam)
        if as_csv:
            csv_string = "## Teams\n"
            csv_string += model_utils.List_To_Csv(
                obj=teams,
                row_header_columns=[
                    prop.FieldName
                    for prop in model_utils.Get_Model_Properties(
                        RootModel_Fixture_Hometeam
                    )
                    if model_utils.Is_Non_Complex_Field_Check_By_Type(prop.FieldType)
                ],
                name="Teams",
            )
            return csv_string
        return teams

    def Get_Home_Team(self) -> RootModel_Fixture_Hometeam:
        return self.Fixture.HomeTeam

    def Get_Away_Team(self) -> RootModel_Fixture_Awayteam:
        return self.Fixture.AwayTeam

    def Get_Innings(self, as_csv: bool = False) -> Any:
        innings = list()
        for inning in self.Innings:
            innings.append(inning)
        if as_csv:
            csv_string = "## Innings\n"
            csv_string += model_utils.List_To_Csv(
                obj=innings,
                row_header_columns=[
                    prop.FieldName
                    for prop in model_utils.Get_Model_Properties(RootModel_Innings)
                    if model_utils.Is_Non_Complex_Field_Check_By_Type(prop.FieldType)
                ],
                name="Innings",
            )
            return csv_string
        return innings

    def Get_Players(self, as_csv: bool = False) -> Any:
        players = list()
        for player in self.Players:
            player_curated = RootModel_Players_Curated(player, self)
            players.append(player_curated)
        if as_csv:
            csv_string = "## Players\n"
            csv_string += model_utils.List_To_Csv(
                obj=players,
                row_header_columns=[
                    prop.FieldName
                    for prop in model_utils.Get_Model_Properties(
                        RootModel_Players_Curated
                    )
                    if model_utils.Is_Non_Complex_Field_Check_By_Type(
                        field_type=prop.FieldType
                    )
                ],
                name="Players",
            )
            return csv_string
        return players

    def Get_Bowlers(self, as_csv: bool = False) -> Any:
        """
        Method to get all the bowlers in the fixture, including their curated stats.
        """
        bowlers = list()
        bowlers_curated_stats = list()
        for innings in [self.Get_Latest_Inning()]:
            for bowler in innings.Bowlers:
                bowler_curated = RootModel_Innings_Bowlers_Extended(bowler, self)
                player_career_stats = self.Get_Player_Career_Stats_By_Id(
                    bowler.PlayerId
                )
                if player_career_stats:
                    bowler_curated_stats = RootModel_Players_Careerstats_Bowlers(
                        player_career_stats, self
                    )
                    bowlers.append(bowler_curated)
                    bowlers_curated_stats.append(bowler_curated_stats)

        if as_csv:
            csv_string = "## Bowlers - Current Innings\n"
            csv_string += model_utils.List_To_Csv(
                obj=bowlers,
                row_header_columns=[
                    prop.FieldName
                    for prop in model_utils.Get_Model_Properties(
                        RootModel_Innings_Bowlers_Extended
                    )
                    if model_utils.Is_Non_Complex_Field_Check_By_Type(
                        field_type=prop.FieldType
                    )
                ],
                name="Bowlers",
            )
            csv_string += "\n\n"
            csv_string += "## Bowlers - Career Performance\n"
            csv_string += model_utils.List_To_Csv(
                obj=bowlers_curated_stats,
                row_header_columns=[
                    prop.FieldName
                    for prop in model_utils.Get_Model_Properties(
                        RootModel_Players_Careerstats_Bowlers
                    )
                    if model_utils.Is_Non_Complex_Field_Check_By_Type(
                        field_type=prop.FieldType
                    )
                ],
                name="Bowlers",
            )
            return csv_string

        return bowlers

    def Get_Batsmen(self, as_csv: bool = False) -> Any:
        """
        Method to get all the batsmen in the fixture
        """
        batsmen = list()
        batsmen_curated_stats = list()
        for innings in [self.Get_Latest_Inning()]:
            for batsman in innings.Batsmen:
                batsman_curated = RootModel_Innings_Batsmen_Extended(batsman, self)

                player_career_stats = self.Get_Player_Career_Stats_By_Id(
                    batsman.PlayerId
                )
                if player_career_stats:
                    batsman_curated_stats = RootModel_Players_Careerstats_Batsmen(
                        player_career_stats, self
                    )
                    batsmen.append(batsman_curated)
                    batsmen_curated_stats.append(batsman_curated_stats)
        if as_csv:
            csv_string = "## Batsmen - Current Innings\n"
            csv_string += model_utils.List_To_Csv(
                obj=batsmen,
                row_header_columns=[
                    prop.FieldName
                    for prop in model_utils.Get_Model_Properties(
                        RootModel_Innings_Batsmen_Extended
                    )
                    if model_utils.Is_Non_Complex_Field_Check_By_Type(
                        field_type=prop.FieldType
                    )
                ],
                name="Batsmen",
            )
            csv_string += "\n\n"
            csv_string += "## Batsmen - Career Performance\n"
            csv_string += model_utils.List_To_Csv(
                obj=batsmen_curated_stats,
                row_header_columns=[
                    prop.FieldName
                    for prop in model_utils.Get_Model_Properties(
                        RootModel_Players_Careerstats_Batsmen
                    )
                    if model_utils.Is_Non_Complex_Field_Check_By_Type(
                        field_type=prop.FieldType
                    )
                ],
                name="Batsmen",
            )
            return csv_string
        return batsmen

    def Get_Current_Batsman_As_Yaml(self) -> Any:
        output = "## Current Batsman\n"

        batsman = self.Get_Current_Batsman()
        if batsman:
            output += model_utils.Object_To_Yaml(batsman)
            return output
        output += "There is No current batsman\n\n"
        return output

    def Get_Current_Batsman(self) -> Optional[RootModel_Innings_Batsmen]:
        inning = self.Get_Latest_Inning()
        for batsman in inning.Batsmen:
            if batsman.IsOnStrike:
                batsman_curated = RootModel_Innings_Batsmen_Extended(batsman, self)
                return batsman_curated
        return None

    def Get_Current_Bowler(self) -> Optional[RootModel_Innings_Bowlers]:
        inning = self.Get_Latest_Inning()
        for bowler in inning.Bowlers:
            if bowler.IsOnStrike:
                return bowler
        return None

    def Get_Player_Career_Stats(self, as_csv: bool = False) -> Any:
        players_cs = list()
        for player in self.Players:
            if player.CareerStats is not None:
                filtered_stats = [
                    stat
                    for stat in player.CareerStats
                    if stat.GameTypeId == self.Fixture.GameTypeId
                ]
                if len(filtered_stats) > 0:
                    players_cs.append(filtered_stats[0])
        if as_csv:
            csv_string = "## Player Career Stats\n"
            csv_string += model_utils.List_To_Csv(
                obj=players_cs,
                row_header_columns=[
                    prop.FieldName
                    for prop in model_utils.Get_Model_Properties(
                        RootModel_Players_Careerstats
                    )
                    if model_utils.Is_Non_Complex_Field_Check_By_Type(prop.FieldType)
                ],
                name="Players",
            )
            return csv_string
        return players_cs

    def Get_Player_Career_Stats_By_Id(self, player_id: Any) -> Any:
        for player in self.Players:
            if player.Id == player_id:
                player.CareerStats
                if player.CareerStats is not None:
                    filtered_stats = [
                        stat
                        for stat in player.CareerStats
                        if stat.GameTypeId == self.Fixture.GameTypeId
                    ]
                    if len(filtered_stats) > 0:
                        return filtered_stats[0]
                else:
                    filtered_stats = RootModel_Players_Careerstats()
                    filtered_stats.PlayerId = player_id
                    filtered_stats.GameTypeId = self.Fixture.GameTypeId
                    return filtered_stats
        return None

    def Get_Team_By_Id(self, team_id) -> Optional[RootModel_Fixture_Hometeam]:
        for team in self.Get_Teams():
            if team.Id == team_id:
                return team
        return None

    def Get_Overs(self, as_csv: bool = False) -> List[RootModel_Innings_Overs_Extended]:
        overs = list()
        for inning in self.Innings:
            overs_for_innings = inning.Get_Overs()
            if overs_for_innings is not None:
                overs.extend(overs_for_innings)

        if as_csv:
            csv_string = model_utils.Listable_Object_To_Csv(
                obj=overs, row_type=RootModel_Innings_Overs_Extended
            )
            return csv_string
        return overs

    class Measure(Enum):
        RUNS = "Runs"
        WICKETS = "Wickets"

    def Get_Overs_Summary(
        self, measure: Measure = Measure.RUNS, as_csv: bool = False
    ) -> Any:
        overs = self.Get_Overs()
        summary = dict()
        teams = self.Get_Teams()
        team_names = [team.Name for team in teams]
        team_innings_tracker = {team.Id: 0 for team in teams}
        headings = ["OverNumber"] + [
            f"{team_name} Innings {innings_number} {measure.value}"
            for team_name in team_names
            for innings_number in (1, 2)
        ]

        for over in overs:
            team_id = over.BattingTeam
            team_name = self.Get_Team_By_Id(team_id).Name

            if self.Get_Inning_By_Number(over.InningsNumber).IsFollowOn:
                team_innings_tracker[team_id] = 2
            else:
                if over.InningsNumber in (1, 2):
                    team_innings_tracker[team_id] = 1
                if over.InningsNumber in (3, 4):
                    team_innings_tracker[team_id] = 2

            if over.OverNumber not in summary:
                summary[over.OverNumber] = {
                    "OverNumber": over.OverNumber,
                    team_names[0] + " Innings 1 " + measure.value: 0,
                    team_names[0] + " Innings 2 " + measure.value: 0,
                    team_names[1] + " Innings 1 " + measure.value: 0,
                    team_names[1] + " Innings 2 " + measure.value: 0,
                }

            innings_number = team_innings_tracker[team_id]
            innings_label = f"{team_name} Innings {innings_number} {measure.value}"
            if measure == self.Measure.RUNS:
                summary[over.OverNumber][innings_label] = over.TotalInningRuns
            elif measure == self.Measure.WICKETS:
                summary[over.OverNumber][innings_label] = over.TotalInningWickets

        # Sort the summary by over number in ascending order
        sorted_summary = dict(sorted(summary.items(), key=lambda item: item[0]))

        if as_csv:
            csv_string = "## Overs Summary\n"
            csv_string += model_utils.Dict_To_Csv(
                obj=sorted_summary, row_header_columns=headings, name="Overs Summary"
            )

            return csv_string

        return sorted_summary

    # Get Aggregate Ball Data for a given player in the match
    def Get_Player_Ball_Data(self, as_csv: bool = False) -> Any:
        summaries_overall = list()
        summaries_length = list()
        summaries_line = list()
        summaries_shot = list()
        summaries_connection = list()
        summaries_shot_placement = list()

        csv_string = ""
        for player in self.Players:
            player_id = player.Id
            player_name = player.DisplayName
            player_balls = list()
            for inning in self.Innings[-1:]:
                for over in inning.Overs:
                    for ball in over.Balls:
                        if (
                            ball.BattingPlayerId == player_id
                            or ball.BowlerPlayerId == player_id
                        ):
                            player_balls.append(ball)

            # Summarize ball data into 1 row for each player
            summary_overall = {
                "PlayerId": player_id,
                "PlayerName": player_name,
                "BallsFaced": sum(
                    1 for ball in player_balls if ball.BattingPlayerId == player_id
                )
                or 0,
                "RunsScored": sum(
                    ball.RunsScored
                    for ball in player_balls
                    if ball.BattingPlayerId == player_id
                )
                or 0,
                "BallsBowled": sum(
                    1 for ball in player_balls if ball.BowlerPlayerId == player_id
                )
                or 0,
                "RunsConceded": sum(
                    ball.RunsConceded
                    for ball in player_balls
                    if ball.BowlerPlayerId == player_id
                )
                or 0,
                "WicketsTaken": sum(
                    1
                    for ball in player_balls
                    if ball.BowlerPlayerId == player_id and ball.IsWicket
                )
                or 0,
            }
            summaries_overall.append(summary_overall)

            # summary_length = {"PlayerId": player_id, "PlayerName": player_name}

            def summarize_measures(
                player_balls,
                player_id,
                player_name,
                measure_name,
                measure_func,
                measure_type_func,
            ):
                summary = {"PlayerId": player_id, "PlayerName": player_name}
                measure_types = measure_type_func()
                for measure in measure_types:
                    summary[f"{measure}_BallsFaced"] = (
                        sum(
                            1
                            for ball in player_balls
                            if ball.BattingPlayerId == player_id
                            and measure_func(getattr(ball, measure_name)) == measure
                        )
                        or 0
                    )
                    summary[f"{measure}_RunsScored"] = (
                        sum(
                            ball.RunsScored
                            for ball in player_balls
                            if ball.BattingPlayerId == player_id
                            and measure_func(getattr(ball, measure_name)) == measure
                        )
                        or 0
                    )
                    summary[f"{measure}_BallsBowled"] = (
                        sum(
                            1
                            for ball in player_balls
                            if ball.BowlerPlayerId == player_id
                            and measure_func(getattr(ball, measure_name)) == measure
                        )
                        or 0
                    )
                    summary[f"{measure}_RunsConceded"] = (
                        sum(
                            ball.RunsConceded
                            for ball in player_balls
                            if ball.BowlerPlayerId == player_id
                            and measure_func(getattr(ball, measure_name)) == measure
                        )
                        or 0
                    )
                    summary[f"{measure}_WicketsTaken"] = (
                        sum(
                            1
                            for ball in player_balls
                            if ball.BowlerPlayerId == player_id
                            and measure_func(getattr(ball, measure_name)) == measure
                            and ball.IsWicket
                        )
                        or 0
                    )
                return summary

            summaries_length.append(
                summarize_measures(
                    player_balls,
                    player_id,
                    player_name,
                    "LengthType",
                    self.Get_Ball_Length_Category,
                    self.Get_Length_Types,
                )
            )
            summaries_line.append(
                summarize_measures(
                    player_balls,
                    player_id,
                    player_name,
                    "LineType",
                    self.Get_Ball_Line_Category,
                    self.Get_Line_Types,
                )
            )
            summaries_connection.append(
                summarize_measures(
                    player_balls,
                    player_id,
                    player_name,
                    "BattingConnection",
                    self.Get_Ball_Shot_Connection_Type_Category,
                    self.Get_Shot_Connection_Types,
                )
            )
            summaries_shot.append(
                summarize_measures(
                    player_balls,
                    player_id,
                    player_name,
                    "BattingShotType",
                    self.Get_Ball_Shot_Type_Category,
                    self.Get_Shot_Types,
                )
            )
            summaries_shot_placement.append(
                summarize_measures(
                    player_balls,
                    player_id,
                    player_name,
                    "ShotAngle",
                    self.Get_Field_Area,
                    self.Get_Field_Areas,
                )
            )

        if as_csv:
            csv_string += "## Player Ball Data - Current Innings High Level Summaries\n"
            csv_string += model_utils.List_To_Csv(
                obj=summaries_overall,
                row_header_columns=summaries_overall[-1].keys(),
                name="Player Ball Data Summary",
            )
            csv_string += "\n\n"
            csv_string += "## Player Ball Data - Current Innings Line Summaries\n"
            csv_string += model_utils.List_To_Csv(
                obj=summaries_line,
                row_header_columns=summaries_line[-1].keys(),
                name="Player Ball Data Summary",
            )
            csv_string += "\n\n"
            csv_string += "## Player Ball Data - Current Length Summaries\n"
            csv_string += model_utils.List_To_Csv(
                obj=summaries_length,
                row_header_columns=summaries_length[-1].keys(),
                name="Player Ball Data Summary",
            )
            csv_string += "\n\n"
            csv_string += "## Player Ball Data - Current Shot Type Summaries\n"
            csv_string += model_utils.List_To_Csv(
                obj=summaries_shot,
                row_header_columns=summaries_shot[-1].keys(),
                name="Player Ball Data Summary",
            )
            csv_string += "\n\n"
            csv_string += "## Player Ball Data - Current Shot Connection Summaries\n"
            csv_string += model_utils.List_To_Csv(
                obj=summaries_connection,
                row_header_columns=summaries_connection[-1].keys(),
                name="Player Ball Data Summary",
            )
            csv_string += "\n\n"
            csv_string += "## Player Ball Data - Current Shot Placement Summaries\n"
            csv_string += model_utils.List_To_Csv(
                obj=summaries_shot_placement,
                row_header_columns=summaries_shot_placement[-1].keys(),
                name="Player Ball Data Summary",
            )
            csv_string += "\n\n"

        return csv_string

    def Get_Length_Types(self) -> Any:
        length_types = set()
        for inning in self.Innings:
            for over in inning.Overs:
                for ball in over.Balls:
                    length_types.add(ball.LengthType)

        length_categories = set()
        for type in length_types:
            length_categories.add(self.Get_Ball_Length_Category(type))
        return length_categories

    def Get_Line_Types(self) -> Any:
        line_types = set()
        for inning in self.Innings:
            for over in inning.Overs:
                for ball in over.Balls:
                    line_types.add(ball.LineType)
        line_categories = set()
        for type in line_types:
            line_categories.add(self.Get_Ball_Line_Category(type))
        return line_categories

    def Get_Shot_Types(self) -> Any:
        shot_types = set()
        for inning in self.Innings:
            for over in inning.Overs:
                for ball in over.Balls:
                    shot_types.add(ball.BattingShotType)
        shot_categories = set()
        for type in shot_types:
            shot_categories.add(self.Get_Ball_Shot_Type_Category(type))
        return shot_categories

    def Get_Shot_Connection_Types(self) -> Any:
        connection_types = set()
        for inning in self.Innings:
            for over in inning.Overs:
                for ball in over.Balls:
                    connection_types.add(ball.BattingConnection)
        connection_categories = set()
        for type in connection_types:
            connection_categories.add(self.Get_Ball_Shot_Connection_Type_Category(type))  # type: ignore[no-untyped-call]
        return connection_categories

    def Get_Field_Areas(self) -> Any:
        """
        Returns a list of all cricket field areas.

        Returns:
            list: A list of strings representing all field areas.
        """
        return [
            "Straight",
            "Off-side",
            "Cover",
            "Mid-wicket",
            "On-side (Leg-side)",
            "Third-man",
        ]

    def Get_Field_Area(self, angle: Any) -> Any:
        """
        Determines the area of a cricket field based on the shot angle.

        Parameters:
            angle (float): The angle of the cricket shot in degrees (0 to 360).

        Returns:
            str: The area of the field corresponding to the angle.
        """
        # Normalize angle to the range [0, 360)
        angle = angle % 360

        if 0 <= angle < 30 or 330 <= angle < 360:
            return "Straight"
        elif 30 <= angle < 90:
            return "Off-side"
        elif 90 <= angle < 150:
            return "Cover"
        elif 150 <= angle < 210:
            return "Mid-wicket"
        elif 210 <= angle < 270:
            return "On-side (Leg-side)"
        elif 270 <= angle < 330:
            return "Third-man"
        else:
            return "Unknown area"

    def Get_Ball_Length_Category(self, ball: Any) -> Any:
        ball = str(ball).replace(" ", "").lower()
        ret = "Unknown"
        match ball:
            case "beamer" | "fulltoss":
                ret = "FullToss"
            case "yorker":
                ret = "Yorker"
            case "halfvolley":
                ret = "HalfVolley"
            case "lengthball" | "backofalength":
                ret = "Length"
            case "short" | "halftracker":
                ret = "Short"
            case _:
                ret = "Unknown"

        if (
            ret == "Unknown"
            and ball != ""
            and ball is not None
            and ball != "none"
            and ball != "null"
        ):
            if self._progress:
                self._progress.progress.print(
                    f"[bold red]❓ Missing shot length category: {ball}[/bold red]"
                )

        return ret

    def Get_Ball_Line_Category(self, line: Any) -> Any:
        line = str(line).replace(" ", "").lower()
        ret = "Unknown"
        match line:
            case "wide" | "widedownleg":
                ret = "Wide"
            case "outsideoff" | "offstump":
                ret = "Outside"
            case "middlestump" | "legstump":
                ret = "Straight"
            case "downleg":
                ret = "Down Leg"
            case _:
                ret = "Unknown"

        if (
            ret == "Unknown"
            and line != ""
            and line is not None
            and line != "none"
            and line != "null"
        ):
            if self._progress:
                self._progress.progress.print(
                    f"[bold red]❓ Missing shot line category: {line}[/bold red]"
                )

        return ret

    def Get_Ball_Shot_Type_Category(self, shot: Any) -> Any:
        shot = str(shot).replace(" ", "")
        ret = "Unknown"
        match shot.lower():
            case "noshot" | "leave" | "padded" | "shouldersarms":
                ret = "Leave"
            case "drive":
                ret = "Drive"
            case "sweep" | "slogsweep":
                ret = "Sweep"
            case "cut" | "uppercut" | "latecut":
                ret = "Cut"
            case "hook" | "pull":
                ret = "Pull"
            case "glance" | "worked" | "pushed" | "flick" | "steer":
                ret = "Worked"
            case "forwarddefensive" | "backwarddefensive" | "fended":
                ret = "Defend"
            case "reversesweep" | "switchhit":
                ret = "Switch Hit"
            case "slog":
                ret = "Left"
            case "dropped":
                ret = "Dropped"
            case "scoop":
                ret = "Scoop"
            case _:
                ret = "Unknown Shot Type"

        if ret == "Unknown":
            if self._progress:
                self._progress.progress.print(
                    f"[bold red]❓ Missing shot category: {shot}[/bold red]"
                )

        return ret

    def Get_Ball_Shot_Connection_Type_Category(self, contact: Any) -> Any:
        contact = str(contact).replace(" ", "")
        ret = "Unknown"
        match contact.lower():
            case "middled" | "welltimed" | "hithard":
                ret = "Middled"
            case (
                "missed"
                | "playandmiss"
                | "missedlegside"
                | "playandmiss(legside)"
                | "playandmisslegside"
            ):
                ret = "Missed"
            case (
                "thickedge"
                | "outsideedge"
                | "insideedge"
                | "topedge"
                | "bottomedge"
                | "batpad"
                | "leadingedge"
                | "edged"
            ):
                ret = "Edged"
            case "padded" | "hitpad":
                ret = "Hit pad"
            case "left" | "noshot" | "shouldersarms":
                ret = "Left"
            case "mistimed" | "mis-timed" | "falseshot" | "spliced":
                ret = "Mis-timed"
            case "none" | "played":
                ret = "None"
            case "hitbody" | "hithelmet":
                ret = "Hit the body"
            case "gloved":
                ret = "Gloved"
            case _:
                ret = "Unknown"

        if ret == "Unknown":
            if self._progress:
                self._progress.progress.print(
                    f"[bold red]❓ Missing shot contact category: {contact}[/bold red]"
                )

        return ret

    def Get_Detail_As_Json(self):
        ret_val = {
            "match_id": self.Fixture.Id,
            "feed_id": self.FeedId,
            "timestamp": self.FeedTimestamp,
            "over_ball": self.Get_Latest_Inning().OversBowled,
            "venue": self.Fixture.Venue.Name,
            "home_team": {
                "id": self.Get_Home_Team().Id,
                "name": self.Get_Home_Team().Name,
            },
            "away_team": {
                "id": self.Get_Away_Team().Id,
                "name": self.Get_Away_Team().Name,
            },
            "batsmen": [self.Get_Current_Batsman()],
            "bowlers": [self.Get_Current_Bowler()],
            "match_status": self.Fixture.GameStatus if self.Fixture else None,
        }

        return ret_val
