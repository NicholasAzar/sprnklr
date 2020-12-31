import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AuthService } from '../auth/auth.service';
import { AppStoreService } from '../client-store/client-store.service';

@Injectable({
  providedIn: 'root'
})
export class TargetsService {
  constructor(private appStore:AppStoreService, private authService:AuthService) {

  }

  get targets():Observable<TargetAccount[]> {
    return this.appStore.getTargetAccounts();
  }

  async addAccount(account:TargetAccount) {
    if (account.accountType == TargetAccountType.GOOGLE) {

    }
  }
}

export enum TargetAccountType {
  LOCAL_PATH,
  GOOGLE
}

export interface LocalTargetAccount {
  path:string;
}

export interface GoogleTargetAccount {
  email:string;
  refreshToken:string;
  accessToken:string;
}

export interface TargetAccount {
  accountType:TargetAccountType;
  account:LocalTargetAccount|GoogleTargetAccount
  lastSync:string;
  active:boolean;
}
