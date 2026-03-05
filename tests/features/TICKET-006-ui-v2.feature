Feature: UI v2 Redesign
  As a runner
  I want a premium looking interface
  To feel more motivated while generating my playlists

  Scenario: Real-time BPM calculation on input
    Given the Flask application is running
    When I enter a pace of "5:00" in the input field
    Then I should see the target BPM updated in the UI

  Scenario: Glassmorphic playlist reveal
    Given the Flask application is running
    When I submit the playlist form with pace "5:00"
    Then I should see track cards with album art placeholders
    And the layout should be modern and glassmorphic
