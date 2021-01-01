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

  addGoogleAccount() {
    return this.authService.login()
      .then((account:Account|void) => {
        if (!account) return;
        const targetAccount = {
          accountType: TargetAccountType.GOOGLE,
          account: {
            email: account.email,
            refreshToken: account.refreshToken,
            accessToken: account.accessToken,
          },
          lastSync: null,
          active: true
        } as TargetAccount<GoogleTargetAccount>;
        // TODO(nzar): do i already have this account added?
        this.appStore.addTargetAccount(targetAccount);
        return targetAccount;
      });
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
