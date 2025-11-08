export type TimeWindow = { date: string; startTime: string; endTime: string; };
export type Court = { id: string; name: string; };
export type Group = { id: string; name: string; size?: number; tags?: string[]; };
export type Constraint = {
  groupId?: string;
  notOverlapWith?: string[];
  earliestStart?: string;
  latestEnd?: string;
  minBreakMinutes?: number;
};
export type PlanRequest = {
  window: TimeWindow;
  courts: Court[];
  groups: Group[];
  slotMinutes: number;
  parallelLimit: number;
  constraints: Constraint[];
  options?: Record<string, any>;
};
export type Slot = {
  start: string; end: string; courtId: string; groupId: string;
  item?: string; judge?: string; comment?: string;
};
export type PlanResponse = { id: string; date: string; slots: Slot[]; };
