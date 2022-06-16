import {IUser} from './user'

export class NullUser implements IUser {
    email: string;
    isNull: () => true;
}
