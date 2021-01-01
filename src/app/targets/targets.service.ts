import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AuthService, Account } from '../auth/auth.service';
import { AppStoreService } from '../client-store/client-store.service';

@Injectable({
  providedIn: 'root'
})
export class TargetsService {
  constructor(private appStore:AppStoreService, private authService:AuthService) {}

  get targets():Observable<TargetAccount[]> {
    return this.appStore.getTargetAccounts();
  }

  getGoogleAccount():Promise<TargetAccount<GoogleTargetAccount>|void> {
    return this.authService.login().then((account) => {
      if (!account) return;
      // TODO(nzar): do i already have this account added?
      return {
        accountType: TargetAccountType.GOOGLE,
        account: {
          email: account.email,
          refreshToken: account.refreshToken,
          accessToken: account.accessToken,
        },
        lastSync: null,
        active: true
      } as TargetAccount<GoogleTargetAccount>;
    });
  }

  persistGoogleAccount(targetAccount:TargetAccount<GoogleTargetAccount>) {
    this.appStore.addTargetAccount(targetAccount);
    return targetAccount;
  }

  persistPath(path:string) {
    this.appStore.addTargetAccount({
      accountType: TargetAccountType.PATH,
      account: {
        path: path
      },
      lastSync: null,
      active: true
    } as TargetAccount<PathTargetAccount>);
  }

  clearAllTargets() {
    this.appStore.clearAllTargetAccounts();
  }
}

export enum TargetAccountType {
  PATH = 'path',
  GOOGLE = 'google'
}

export interface PathTargetAccount {
  path:string;
}

export interface GoogleTargetAccount {
  email:string;
  refreshToken:string;
  accessToken:string;
}

export interface TargetAccount<T = GoogleTargetAccount|PathTargetAccount|void> {
  accountType:TargetAccountType;
  account:T;
  lastSync:string;
  active:boolean;
}
