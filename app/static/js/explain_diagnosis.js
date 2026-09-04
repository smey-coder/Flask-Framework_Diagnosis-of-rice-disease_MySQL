function filterSelectedSymptoms() {
    const input = document.getElementById('symptomSearchInput');
    const filter = input.value.toLowerCase();
    const chips = document.querySelectorAll('#symptomBadgeContainer .symptom-chip');

    chips.forEach(chip => {
      const text = chip.querySelector('.symptom-text').textContent || '';
      if (text.toLowerCase().indexOf(filter) > -1) {
        chip.style.setProperty('display', 'inline-flex', 'important');
      } else {
        chip.style.setProperty('display', 'none', 'important');
      }
    });
  }