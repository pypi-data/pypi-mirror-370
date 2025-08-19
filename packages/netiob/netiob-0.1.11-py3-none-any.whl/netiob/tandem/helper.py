from typing import Optional

from pandas import DataFrame


class TandemHelper:
    id: str
    df_LidBasalRateChange: Optional[DataFrame] = None
    df_LidPumpingSuspended: Optional[DataFrame] = None
    df_LidPumpingResumed: Optional[DataFrame] = None
    df_LidBgReadingTaken: Optional[DataFrame] = None
    df_LidBolusCompleted: Optional[DataFrame] = None
    df_LidBolexCompleted: Optional[DataFrame] = None
    df_LidBolusActivated: Optional[DataFrame] = None
    df_LidBolexActivated: Optional[DataFrame] = None
    df_LidCgmDataGxb: Optional[DataFrame] = None
    df_LidBasalDelivery: Optional[DataFrame] = None
    df_LidBolusDelivery: Optional[DataFrame] = None
    df_LidAaDailyStatus: Optional[DataFrame] = None
    df_LidCgmDataFsl2: Optional[DataFrame] = None
    df_LidCgmDataG7: Optional[DataFrame] = None
    df_LidDailyBasal: Optional[DataFrame] = None
    df_LidCarbsEntered: Optional[DataFrame] = None

    def __init__(
            self,
            id: str,
            df_LidBasalRateChange: Optional[DataFrame] = None,
            df_LidPumpingSuspended: Optional[DataFrame] = None,
            df_LidPumpingResumed: Optional[DataFrame] = None,
            df_LidBgReadingTaken: Optional[DataFrame] = None,
            df_LidBolusCompleted: Optional[DataFrame] = None,
            df_LidBolexCompleted: Optional[DataFrame] = None,
            df_LidBolusActivated: Optional[DataFrame] = None,
            df_LidBolexActivated: Optional[DataFrame] = None,
            df_LidCgmDataGxb: Optional[DataFrame] = None,
            df_LidBasalDelivery: Optional[DataFrame] = None,
            df_LidBolusDelivery: Optional[DataFrame] = None,
            df_LidAaDailyStatus: Optional[DataFrame] = None,
            df_LidCgmDataFsl2: Optional[DataFrame] = None,
            df_LidCgmDataG7: Optional[DataFrame] = None,
            df_LidDailyBasal: Optional[DataFrame] = None,
            df_LidCarbsEntered: Optional[DataFrame] = None
    ):
        self.id = id
        self.df_LidBasalRateChange = df_LidBasalRateChange
        self.df_LidPumpingSuspended = df_LidPumpingSuspended
        self.df_LidPumpingResumed = df_LidPumpingResumed
        self.df_LidBgReadingTaken = df_LidBgReadingTaken
        self.df_LidBolusCompleted = df_LidBolusCompleted
        self.df_LidBolexCompleted = df_LidBolexCompleted
        self.df_LidBolusActivated = df_LidBolusActivated
        self.df_LidBolexActivated = df_LidBolexActivated
        self.df_LidCgmDataGxb = df_LidCgmDataGxb
        self.df_LidBasalDelivery = df_LidBasalDelivery
        self.df_LidBolusDelivery = df_LidBolusDelivery
        self.df_LidAaDailyStatus = df_LidAaDailyStatus
        self.df_LidCgmDataFsl2 = df_LidCgmDataFsl2
        self.df_LidCgmDataG7 = df_LidCgmDataG7
        self.df_LidDailyBasal = df_LidDailyBasal
        self.df_LidCarbsEntered = df_LidCarbsEntered
