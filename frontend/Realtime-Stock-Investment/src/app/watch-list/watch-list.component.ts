import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';

@Component({
  selector: 'app-watch-list',
  templateUrl: './watch-list.component.html',
  styleUrl: './watch-list.component.css'
})
export class WatchListComponent {
  marketData = [
    { market: 'GARAN', change: 0.15, last: 302.75, high: 311.50, low: 302.50, open: 300.0, volume: '432.5M', time: '17:45:05' },
    { market: 'AKBNK', change: -0.15, last: 302.60, high: 311.40, low: 302.30, open: 299.8, volume: '430.0M', time: '17:45:05' },
    { market: 'ISCTR', change: 0.30, last: 303.00, high: 312.00, low: 303.00, open: 300.5, volume: '435.0M', time: '17:45:05' },
    { market: 'YKBNK', change: -0.20, last: 302.55, high: 311.25, low: 302.00, open: 299.9, volume: '431.5M', time: '17:45:05' },
    { market: 'VAKBN', change: 0.10, last: 302.80, high: 311.60, low: 302.50, open: 300.2, volume: '432.8M', time: '17:45:05' },
    { market: 'HALKB', change: -0.25, last: 302.50, high: 311.20, low: 302.10, open: 299.7, volume: '430.2M', time: '17:45:05' },
    { market: 'TUPRS', change: 0.05, last: 302.70, high: 311.40, low: 302.40, open: 300.1, volume: '432.3M', time: '17:45:05' },
    { market: 'EREGL', change: -0.10, last: 302.65, high: 311.35, low: 302.25, open: 299.5, volume: '431.0M', time: '17:45:05' },
    { market: 'PETKM', change: 0.25, last: 302.90, high: 311.70, low: 302.60, open: 300.3, volume: '433.0M', time: '17:45:05' },
    { market: 'SAHOL', change: -0.05, last: 302.75, high: 311.50, low: 302.50, open: 299.9, volume: '432.5M', time: '17:45:05' }
  ];

  searchControl = new FormControl();
  filteredOptions: string[] = [];
  allOptions: string[] = ['GARAN', 'AKBNK', 'ISCTR', 'YKBNK', 'VAKBN', 'HALKB', 'TUPRS', 'EREGL', 'PETKM', 'SAHOL'];

  constructor(private http: HttpClient) { }

  ngOnInit(): void {
    // Fetch options from backend
    
    this.filteredOptions = this.allOptions;

    this.searchControl.valueChanges.pipe(
      startWith(''),
      map(value => this._filter(value))
    ).subscribe(filtered => this.filteredOptions = filtered);
  }

  private _filter(value: string): string[] {
    const filterValue = value.toLowerCase();
    return this.allOptions.filter(option => option.toLowerCase().includes(filterValue));
  }

  onOptionSelected(event: any): void {
    const selectedMarket = event.option.value;
    this.addRow(selectedMarket);
  }

  addRow(market: string): void {
    // Add new market row with default values
    this.marketData.push({
      market: market,
      change: 0.00,  // Default value
      last: 0.00,    // Default value
      high: 0.00,    // Default value
      low: 0.00,     // Default value
      open: 0.00,    // Default value
      volume: '0.0M', // Default value
      time: new Date().toLocaleTimeString() // Default to current time
    });
  }

  deleteRow(index: number): void {
    this.marketData.splice(index, 1);
  }
}
