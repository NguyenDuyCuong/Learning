export interface IUser {
    email: string;
    isNull(): boolean;
}

export class User implements IUser {
    email: string;
    isNull(): boolean { return false; }
}
