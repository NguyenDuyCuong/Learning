import { NullUser } from '../types/null-user';
import {Requests} from '../types/requests';
import {IUser} from '../types/user';

export class UserStoreState {
    user: IUser = new NullUser();
    requests: Requests = {
        getUser: {},
    };
}
