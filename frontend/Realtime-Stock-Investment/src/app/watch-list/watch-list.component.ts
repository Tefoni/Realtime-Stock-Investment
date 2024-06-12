import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { Observable, Subscription, interval } from 'rxjs';
import { map, startWith } from 'rxjs/operators';
import { StockInvestmentService } from '../services/stock-investment.service';

@Component({
  selector: 'app-watch-list',
  templateUrl: './watch-list.component.html',
  styleUrl: './watch-list.component.css'
})
export class WatchListComponent {
  private updateSubscription!: Subscription;
  marketData = [];
  marketNames: string[] = [];

  searchControl = new FormControl();
  filteredOptions: string[] = [];
  allOptions: string[] = ['GARAN', 'AKBNK', 'ISCTR', 'YKBNK', 'VAKBN', 'HALKB', 'TUPRS', 'EREGL', 'PETKM', 'SAHOL'];

  constructor(private service: StockInvestmentService) { }


  ngOnInit(){
    this.service.getStockSymbols().subscribe(response => {
      if(response.isSuccessful){
        this.allOptions = response.message;
        this.allOptions = response.message.map((option: string) => option.replace('.IS', ''));
        this.filteredOptions = this.allOptions;
      }
      else{
        this.service.showSnackBar(response.message,'error');
      }
    });
    this.searchControl.valueChanges.pipe(
      startWith(''),
      map(value => this._filter(value))
    ).subscribe(filtered => this.filteredOptions = filtered);

    this.service.getWatchList().subscribe(response => {
      if(response.isSuccessful){
        this.marketNames = response.message;
        this.service.getMarketStocks(this.marketNames).subscribe(response => {
          if(response.isSuccessful){
            this.marketData = response.message;
          }
          else{
            this.service.showSnackBar(response.message,'error');
          }
        });
      }
      else{
        this.service.showSnackBar(response.message,'error');
      }
    });

    this.updateSubscription = interval(5000).subscribe(() => {
      this.service.getMarketStocks(this.marketNames).subscribe(response => {
        if(response.isSuccessful){
          this.marketData = response.message;
        }
        else{
          this.service.showSnackBar(response.message,'error');
        }
      });
    });

  }

  ngOnDestroy(){
    if (this.updateSubscription) {
      this.updateSubscription.unsubscribe();
    }
  }

  private _filter(value: string): string[] {
    const filterValue = value.toLowerCase();
    return this.allOptions.filter(option => option.toLowerCase().includes(filterValue));
  }

  onOptionSelected(event: any): void {
    const selectedMarket = event.option.value;
    this.marketNames.push(selectedMarket + ".IS");

    this.service.addWatchListStock(selectedMarket+ ".IS").subscribe(response => {
      if(response.isSuccessful){
        this.service.getMarketStocks(this.marketNames).subscribe(response => {
          if(response.isSuccessful){
            this.marketData = response.message;
          }
          else{
            this.service.showSnackBar(response.message,'error');
          }
        });
      }
      else{
        this.service.showSnackBar(response.message,'error');
      }
    });
  }

  deleteRow(index: number): void {
    this.service.removeWatchListStock(this.marketNames[index]).subscribe(response => {
      if(response.isSuccessful){
        this.marketNames.splice(index,1);
        this.service.getMarketStocks(this.marketNames).subscribe(response => {
          if(response.isSuccessful){
            this.marketData = response.message;
          }
          else{
            this.service.showSnackBar(response.message,'error');
          }
        });
      }
      else{
        this.service.showSnackBar(response.message,'error');
      }
    });
    
  }
}
