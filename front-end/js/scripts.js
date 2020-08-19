/*!
 * Start Bootstrap - Freelancer v6.0.4 (https://startbootstrap.com/themes/freelancer)
 * Copyright 2013-2020 Start Bootstrap
 * Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-freelancer/blob/master/LICENSE)
 */
(function($) {
    "use strict"; // Start of use strict



    // Smooth scrolling using jQuery easing
    $('a.js-scroll-trigger[href*="#"]:not([href="#"])').click(function() {
        if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
            var target = $(this.hash);
            target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
            if (target.length) {
                $('html, body').animate({
                    scrollTop: (target.offset().top - 71)
                }, 1000, "easeInOutExpo");
                return false;
            }
        }
    });

    // Scroll to top button appear
    $(document).scroll(function() {
        var scrollDistance = $(this).scrollTop();
        if (scrollDistance > 100) {
            $('.scroll-to-top').fadeIn();
        } else {
            $('.scroll-to-top').fadeOut();
        }
    });

    // Closes responsive menu when a scroll trigger link is clicked
    $('.js-scroll-trigger').click(function() {
        $('.navbar-collapse').collapse('hide');
    });

    // Activate scrollspy to add active class to navbar items on scroll
    $('body').scrollspy({
        target: '#mainNav',
        offset: 80
    });

    // Collapse Navbar
    var navbarCollapse = function() {
        if ($("#mainNav").offset().top > 100) {
            $("#mainNav").addClass("navbar-shrink");
        } else {
            $("#mainNav").removeClass("navbar-shrink");
        }
    };
    // Collapse now if page is not at top
    navbarCollapse();
    // Collapse the navbar when page is scrolled
    $(window).scroll(navbarCollapse);

    // Floating label headings for the contact form
    $(function() {
        $("body").on("input propertychange", ".floating-label-form-group", function(e) {
            $(this).toggleClass("floating-label-form-group-with-value", !!$(e.target).val());
        }).on("focus", ".floating-label-form-group", function() {
            $(this).addClass("floating-label-form-group-with-focus");
        }).on("blur", ".floating-label-form-group", function() {
            $(this).removeClass("floating-label-form-group-with-focus");
        });
    });

})(jQuery); // End of use strict


// Get the data
$(document).ready(function() {
    var request = new XMLHttpRequest();
    var hours;
    var pm10;
    request.open('GET', 'https://api.svifryk.is/getPM10', true);
    request.onload = function() {

        // Begin accessing JSON data here
        var data = JSON.parse(this.response);
        labels = [];
        datad = [];
        if (request.status >= 200 && request.status < 400) {
            data.forEach(object => {
                var valid_time = `${object.valid_time}`;
                var forecast_time = `${object.forecast_time}`;
                var myDate = new Date(valid_time);
                hours = myDate.getHours();
                pm10 = `${object.pm10}`;
                pm10 = parseInt(pm10);
                labels.push(hours);
                datad.push(pm10);
            });
        } else {
            console.log("Gah, it's not working!");
        }
        max_pm = Math.max(...datad);
        //if (max_pm % 20 > 14 || max_pm % 20 == 0) {
        max_pm = (Math.floor(max_pm / 20) + 2) * 20;
        console.log(max_pm);

        // Calculate maximum values for next days
        var value_array = [];
        labels.forEach(function(v, i) {
            var obj = {};
            obj.hour = v;
            obj.value = datad[i];
            value_array.push(obj);
        });

        var day_values = [];
	var values = [];
        for (i = 0; i < value_array.length; i++) {
            if (value_array[i].hour < 23) {
                values.push(value_array[i].value);
            } else {
                day_values.push(Math.max.apply(Math, values));
                values = [];
            }
        }
        day_values.push(Math.max.apply(Math, values));

        // Set values in the forecast  
        var box = document.getElementsByClassName("colorbox");
        var boxwords = document.getElementsByClassName("colorboxname");
        for (i = 0; i < 3; i++) {

            // Sort green, yellow, red		
            if (day_values[i] < 50) {
                box[i].style.background = "#45b39b";
                var text = document.createTextNode("GOTT");
                boxwords[i].appendChild(text);
            } else if (day_values[i] < 100) {
                box[i].style.background = "#efc94a";
                var text = document.createTextNode("Í LAGI");
                boxwords[i].appendChild(text);
            } else {
                box[i].style.background = "#e05b49";
                var text = document.createTextNode("SLÆMT");
                boxwords[i].appendChild(text);
            }
            var text = document.createTextNode(day_values[i] + " µg/m³");
            box[i].appendChild(text);
        }


        // Create the chart
        new Chart(document.getElementById("line-chart"), {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    data: datad,
                    borderColor: "#212529",
                    fill: true
                }, {
                    data: [50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50],
                    borderColor: "#efc94a",
                    pointRadius: 0,
                    fill: false
                }, {
                    data: [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
                    borderColor: "#e05b49",
                    pointRadius: 0,
                    fill: false
                }]
            },
            options: {
                legend: {
                    display: false,
                },
                scales: {
                    yAxes: [{
                        scaleLabel: {
                            display: true,
                            labelString: "µg/m³"
                        },
                        ticks: {
                            min: 0,
                            max: max_pm
                        }
                    }]
                }
            }
        });
    }

    request.send();

});
