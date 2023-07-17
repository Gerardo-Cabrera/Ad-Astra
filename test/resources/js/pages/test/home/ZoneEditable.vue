<template>
  <div class="zone-editable">
    <div
      v-if="display"
      class="zone-display"
    >
      <div>
        Zone Name: <strong>{{ name }}</strong> Distributions: {{ distributionDisplay }}
      </div>

      <button
        class="btn btn-primary"
        @click="setDisplay(false)"
        :disabled="saving"
      >
        Edit
      </button>
    </div>
    <div
      v-else
      class="zone-edit"
    >
      <label class="control-label">
        Zone Name
      </label>

      <input
        :name="name"
        v-model="form.name"
        placeholder="Zone name"
        class="form-control zone-name"
        :disabled="saving"
        @input="validateName"
      >

      <div class="zone-edit-distributions">
        <div v-for="distribution in form.distributions" :key="distribution.id">
          <label class="control-label">
            Distribution
          </label>
          <input
            :id="distribution.id"
            v-model="distribution.percentage"
            placeholder="Percentage"
            class="form-control"
            type="number"
            @input="validatePercentage(distribution.percentage)"
            required
          >
          <button class="btn btn-danger" @click="removeDistribution(distribution.id)" :disabled="saving">
            Remove
          </button>
        </div>
      </div>
      
      <div class="zone-edit-actions">
        <button class="btn btn-primary" @click="addDistribution" :disabled="saving">
          Add distribution
        </button>
        <button
          class="btn btn-secondary"
          @click="setDisplay(true)"
          :disabled="saving"
        >
         Cancel
        </button>

        <button
          class="btn btn-success"
          @click="save"
          :disabled="saving"
        >
          Save
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ZoneEditable',
  props: {
    name: String,
    id: Number,
    distributions: Array,
  },
  data() {
    return {
      display: true,
      form: {
        name: '',
        distributions: [],
      },
      saving: false,
      url: '/api/zones/'
    };
  },
  computed: {
    distributionDisplay() {
      return this.distributions.map(distribution => distribution.percentage + "%").join('-');
    }
  },
  mounted() {
    this.getValuesFromProps();
  },
  methods: {
    addDistribution() {
      this.form.distributions.push({
        id: '',
        percentage: '',
      });
    },
    getValuesFromProps(value=false) {
      this.form.name = this.name;
      if (!value) {
        this.form.distributions = this.distributions.map(distribution => Object.assign({}, distribution));
      } else {
        this.distributions = this.form.distributions.map(distribution => Object.assign({}, distribution));
      }
    },
    setDisplay(value) {
      this.display = value;

      if(!this.display) {
        this.getValuesFromProps();
      }
    },
    validatePercentage(percentage) {
      const percentageRegex = /^\d+$/;
      
      if (!percentageRegex.test(percentage)) {
        percentage = '';
      } else {
        percentage = parseInt(percentage);
      }

      if (percentage < 0) {
        percentage = 0;
      } else if (percentage > 100) {
        percentage = 100;
      }

      return percentage;
    },
    getZoneNamesFromInputs() {
      const zoneNameInputs = document.querySelectorAll('.zone-name');
      const zoneNames = Array.from(zoneNameInputs).map(input => input.value.trim());
      return zoneNames;
    },
    hasDuplicateZoneName(name) {
      const zoneNameInputs = document.querySelectorAll('.zone-edit .zone-name');
      const zoneNames = [];

      zoneNameInputs.forEach(input => {
        zoneNames.push(input.value.trim());
      });

      return zoneNames;
    },
    validateName(name) {
      const nameRegex = /^[a-zA-Z0-9]+( [a-zA-Z0-9]+)*$/;

      if (!nameRegex.test(name)) {
        alert('Invalid zone name. It must not be empty, cannot have more than one space between words, and cannot have spaces at the start or end.');
        name = '';
        return;
      }

      return name.trim() !== '' && name === name.trim();
    },
    validateForm() {
      const errors = [];

      if (!this.validateName(this.form.name)) {
        errors.push('Invalid zone name.');
      }

      const distributionNames = new Set();
      let totalPercentage = 0;

      for (const distribution of this.form.distributions) {
        const percentage = this.validatePercentage(distribution.percentage);

        if (!percentage) {
          errors.push('Invalid percentage in distribution.');
        }

        totalPercentage += percentage;

        if (distributionNames.has(distribution.id)) {
          errors.push('Duplicate distribution ID.');
        } else {
          distributionNames.add(distribution.id);
        }
      }

      if (totalPercentage !== 100) {
        errors.push('The sum of all distributions must be 100%.');
      }

      return errors;
    },
    async save() {
      this.saving = true;

      const validationErrors = this.validateForm();
      if (validationErrors.length > 0) {
        alert(validationErrors.join('\n'));
        this.saving = false;
        return;
      }

      const params = {
        id: this.id,
        name: this.form.name,
        distributions: this.form.distributions
      };

      await axios.post(this.url + 'edit', params);

      this.$emit('edit', {name: params.name});

      this.saving = false;
      this.display = true;

      this.getValuesFromProps(true);
    },
    async removeDistribution(id) {
      try {
        await axios.delete(this.url + 'delete/' + id);
        const index = this.form.distributions.findIndex(distribution => distribution.id === id);
        if (index !== -1) {
          this.form.distributions.splice(index, 1);
        }
      } catch (error) {
        console.error('Error while deleting distribution:', error);
      }
    },
  }
}
</script>

<style lang="scss">
@import 'resources/scss/variables.scss';

.zone-editable {
  border: 1px solid $gray-color;
  padding: $qmb;
  border-radius: $border-radius;

  .zone-display {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .zone-edit {
    display: flex;
    flex-direction: column;
    gap: $small-action-space;

    .zone-edit-actions {
      display: flex;
      gap: $small-action-space;
      justify-content: end;
    }

    .zone-edit-distributions {
      display: grid;
      grid-template-columns: repeat(1, 1fr);
      gap: $small-action-space;
    }
  }
}
</style>
