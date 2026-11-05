<template>
  <div class="restocking">
    <div class="page-header">
      <h1>{{ t('restocking.title') }}</h1>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="!recommendation" class="error">{{ error }}</div>
    <div v-else>
      <div class="card">
        <label class="slider-label" for="budget-slider">
          <span>{{ t('restocking.budget') }}</span>
          <strong>{{ money(budget) }}</strong>
        </label>
        <input
          id="budget-slider"
          v-model.number="budget"
          class="budget-slider"
          type="range"
          min="0"
          :max="fullCost"
          step="0.01"
          :aria-valuetext="money(budget)"
          @change="loadRecommendations"
        />
        <div class="slider-bounds">
          <span>{{ money(0) }}</span>
          <span>{{ t('restocking.fullCost') }}: {{ money(fullCost) }}</span>
        </div>
      </div>

      <div v-if="error" class="error">{{ error }}</div>

      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.budget') }}</div>
          <div class="stat-value">{{ money(recommendation.budget) }}</div>
        </div>
        <div class="stat-card info">
          <div class="stat-label">{{ t('restocking.totalCost') }}</div>
          <div class="stat-value">{{ money(recommendation.total_cost) }}</div>
        </div>
        <div class="stat-card success">
          <div class="stat-label">{{ t('restocking.remainingBudget') }}</div>
          <div class="stat-value">{{ money(recommendation.remaining_budget) }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.recommendations') }} ({{ recommendation.items.length }})</h3>
          <button
            class="place-order"
            type="button"
            :disabled="!recommendation.items.length || submitting || refreshing"
            @click="placeOrder"
          >
            {{ submitting ? t('restocking.placingOrder') : t('restocking.placeOrder') }}
          </button>
        </div>

        <p v-if="placedOrder" class="confirmation" role="status">
          {{ t('restocking.orderPlaced', { orderNumber: placedOrder.order_number }) }}
          <router-link to="/orders">{{ t('restocking.viewOrders') }}</router-link>
        </p>
        <p v-if="orderError" class="error" role="alert">{{ orderError }}</p>

        <p v-if="!recommendation.items.length" class="empty">{{ t('restocking.noRecommendations') }}</p>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('restocking.table.item') }}</th>
                <th>{{ t('restocking.table.trend') }}</th>
                <th class="num">{{ t('restocking.table.quantity') }}</th>
                <th class="num">{{ t('restocking.table.unitCost') }}</th>
                <th class="num">{{ t('restocking.table.lineTotal') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in recommendation.items" :key="item.sku">
                <td><strong>{{ translateProductName(item.name) }}</strong></td>
                <td>
                  <span :class="['badge', item.trend]">{{ t(`trends.${item.trend}`) }}</span>
                </td>
                <td class="num">{{ quantityLabel(item) }}</td>
                <td class="num">{{ money(item.unit_cost) }}</td>
                <td class="num"><strong>{{ money(item.line_total) }}</strong></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'
import { formatCurrencyWithDecimals } from '../utils/currency'

export default {
  name: 'Restocking',
  setup() {
    const { t, currentCurrency, translateProductName } = useI18n()

    const loading = ref(true)
    const refreshing = ref(false)
    const submitting = ref(false)
    const error = ref(null)
    const orderError = ref(null)
    const placedOrder = ref(null)
    const recommendation = ref(null)
    const fullCost = ref(0)
    const budget = ref(0)

    // Cents matter for the slider and unit costs, so every amount shows two decimals in USD
    const money = (amount) => formatCurrencyWithDecimals(amount, currentCurrency.value, 2)

    const quantityLabel = (item) => {
      return item.quantity < item.quantity_needed
        ? t('restocking.ofNeeded', { quantity: item.quantity, needed: item.quantity_needed })
        : String(item.quantity)
    }

    // Only the newest request may write results, so a slow earlier response cannot overwrite a later one
    let latestRequest = 0
    const loadRecommendations = async () => {
      const requestId = ++latestRequest
      refreshing.value = true
      try {
        const result = await api.getRestockRecommendations(budget.value)
        if (requestId !== latestRequest) return
        recommendation.value = result
        error.value = null
      } catch (err) {
        if (requestId !== latestRequest) return
        error.value = t('restocking.loadFailed') + ': ' + err.message
      } finally {
        if (requestId === latestRequest) refreshing.value = false
      }
    }

    // A budget of 0 buys nothing but still returns full_cost, which sets the slider range
    const loadInitial = async () => {
      try {
        const { full_cost } = await api.getRestockRecommendations(0)
        fullCost.value = full_cost
        budget.value = Math.round(full_cost * 50) / 100
        await loadRecommendations()
      } catch (err) {
        error.value = t('restocking.loadFailed') + ': ' + err.message
      } finally {
        loading.value = false
      }
    }

    const placeOrder = async () => {
      submitting.value = true
      placedOrder.value = null
      orderError.value = null
      try {
        placedOrder.value = await api.createRestockOrder(budget.value)
        await loadRecommendations()
      } catch (err) {
        const detail = err.response?.data?.detail
        orderError.value = typeof detail === 'string' ? detail : t('restocking.orderFailed')
      } finally {
        submitting.value = false
      }
    }

    onMounted(loadInitial)

    return {
      t,
      loading,
      refreshing,
      submitting,
      error,
      orderError,
      placedOrder,
      recommendation,
      fullCost,
      budget,
      money,
      quantityLabel,
      loadRecommendations,
      placeOrder,
      translateProductName
    }
  }
}
</script>

<style scoped>
.slider-label {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 0.75rem;
  color: var(--color-text-muted);
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.slider-label strong {
  color: var(--color-text-strong);
  font-size: 1.5rem;
  letter-spacing: -0.025em;
}

.budget-slider {
  width: 100%;
  accent-color: var(--color-text-strong);
}

.slider-bounds {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  color: var(--color-text-muted);
  font-size: 0.813rem;
}

.place-order {
  padding: 0.5rem 1.25rem;
  background: var(--color-text-strong);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
}

.place-order:hover:not(:disabled) {
  background: #1e293b;
}

.place-order:disabled {
  background: var(--color-border-strong);
  cursor: not-allowed;
}

.confirmation {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #166534;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-size: 0.938rem;
}

.confirmation a {
  margin-left: 0.5rem;
  color: var(--color-primary);
  font-weight: 600;
}

.empty {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-muted);
  font-size: 0.938rem;
}

.num {
  text-align: right;
}
</style>
