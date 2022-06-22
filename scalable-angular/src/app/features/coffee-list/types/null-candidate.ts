import { RequestState } from "@app/shared/types/request-state";
import { UserAction } from "../coffee-list.constants";
import { ICandidate } from "./candidate";
import { Vote } from "./vote";

export class NullCandidate implements ICandidate {
    id: number;
    name: string;
    votes: Vote[];
    userAction?: UserAction;
    updateRequest?: RequestState;
    
    isNull: () => true;
}
