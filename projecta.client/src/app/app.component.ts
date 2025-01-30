import { HttpClient } from '@angular/common/http';
import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup } from '@angular/forms';

interface WeatherForecast {
  date: string;
  temperatureC: number;
  temperatureF: number;
  summary: string;
}

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  standalone: false,
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit {
  public forecasts: WeatherForecast[] = [];
  controls: any[] = [];
  form: FormGroup;
  showControls!:boolean;

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private cdf:ChangeDetectorRef
  )
  {
    this.form = this.fb.group({});
  }

  ngOnInit() {
    this.getForecasts();
    this.getLayout();
  }

  ngAfterViewInit() {
  }

  getForecasts() {
    this.http.get<WeatherForecast[]>('/weatherforecast/GetWeatherForecast').subscribe({
      next: (result) => {
        this.forecasts = result;
        this.cdf.detectChanges();
      },
      error: (error) => {
        console.error(error);
      },
      complete: () => {

      }
    });
  }

  getLayout() {
    this.http.get<any>('/weatherforecast/GetLayout').subscribe({
      next: (result) => {
        this.controls = result.controls;
        this.controls.forEach(control =>
          { this.form.addControl(control.name, new FormControl('')); }
        );
        console.log(this.controls);
        this.showControls = true;
        this.cdf.detectChanges();
      },
      error: (error) => {
        console.error(error);
      },
      complete: () => {

      }
    });
  }

  title = 'projecta.client';
}
