/**
 * Service Worker pour Lataupe Bunker Tech
 * Gestion du cache et fonctionnalités hors ligne
 */

const CACHE_NAME = 'bunker-tech-v2.0.0';
const STATIC_CACHE = 'bunker-static-v2.0.0';
const DYNAMIC_CACHE = 'bunker-dynamic-v2.0.0';

// Fichiers à mettre en cache immédiatement
const STATIC_FILES = [
  '/',
  '/static/css/responsive.css',
  '/static/js/mobile.js',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  '/offline.html'
];

// Fichiers à mettre en cache dynamiquement
const DYNAMIC_FILES = [
  '/dashboard',
  '/quiz',
  '/profile',
  '/settings'
];

// Installation du Service Worker
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installation');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('Service Worker: Mise en cache des fichiers statiques');
        return cache.addAll(STATIC_FILES);
      })
      .then(() => {
        return self.skipWaiting();
      })
  );
});

// Activation du Service Worker
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activation');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
              console.log('Service Worker: Suppression ancien cache', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        return self.clients.claim();
      })
  );
});

// Interception des requêtes
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Ignorer les requêtes non-HTTP
  if (!request.url.startsWith('http')) {
    return;
  }
  
  // Stratégie Cache First pour les ressources statiques
  if (isStaticResource(request)) {
    event.respondWith(cacheFirst(request));
    return;
  }
  
  // Stratégie Network First pour les API
  if (isApiRequest(request)) {
    event.respondWith(networkFirst(request));
    return;
  }
  
  // Stratégie Stale While Revalidate pour les pages
  if (isPageRequest(request)) {
    event.respondWith(staleWhileRevalidate(request));
    return;
  }
  
  // Par défaut, essayer le réseau puis le cache
  event.respondWith(networkFirst(request));
});

// Vérifier si c'est une ressource statique
function isStaticResource(request) {
  const url = new URL(request.url);
  return url.pathname.includes('/static/') || 
         url.pathname.includes('/icons/') ||
         url.pathname.endsWith('.css') ||
         url.pathname.endsWith('.js') ||
         url.pathname.endsWith('.png') ||
         url.pathname.endsWith('.jpg') ||
         url.pathname.endsWith('.svg');
}

// Vérifier si c'est une requête API
function isApiRequest(request) {
  const url = new URL(request.url);
  return url.pathname.startsWith('/api/') || 
         url.pathname.startsWith('/auth/');
}

// Vérifier si c'est une requête de page
function isPageRequest(request) {
  return request.method === 'GET' && 
         request.headers.get('accept').includes('text/html');
}

// Stratégie Cache First
async function cacheFirst(request) {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Cache First Error:', error);
    return caches.match('/offline.html');
  }
}

// Stratégie Network First
async function networkFirst(request) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Network First Error:', error);
    
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Retourner une page hors ligne pour les requêtes de page
    if (isPageRequest(request)) {
      return caches.match('/offline.html');
    }
    
    // Retourner une réponse d'erreur pour les API
    return new Response(
      JSON.stringify({ error: 'Pas de connexion réseau' }),
      {
        status: 503,
        statusText: 'Service Unavailable',
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Stratégie Stale While Revalidate
async function staleWhileRevalidate(request) {
  const cache = await caches.open(DYNAMIC_CACHE);
  const cachedResponse = await cache.match(request);
  
  const fetchPromise = fetch(request).then((networkResponse) => {
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  }).catch(() => {
    // En cas d'erreur réseau, retourner la version en cache
    return cachedResponse || caches.match('/offline.html');
  });
  
  // Retourner immédiatement la version en cache si disponible
  return cachedResponse || fetchPromise;
}

// Gestion des messages du client
self.addEventListener('message', (event) => {
  const { type, payload } = event.data;
  
  switch (type) {
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;
      
    case 'GET_CACHE_SIZE':
      getCacheSize().then((size) => {
        event.ports[0].postMessage({ type: 'CACHE_SIZE', payload: size });
      });
      break;
      
    case 'CLEAR_CACHE':
      clearCache().then(() => {
        event.ports[0].postMessage({ type: 'CACHE_CLEARED' });
      });
      break;
      
    case 'SYNC_DATA':
      // Synchroniser les données hors ligne
      syncOfflineData(payload);
      break;
  }
});

// Obtenir la taille du cache
async function getCacheSize() {
  const cacheNames = await caches.keys();
  let totalSize = 0;
  
  for (const cacheName of cacheNames) {
    const cache = await caches.open(cacheName);
    const requests = await cache.keys();
    
    for (const request of requests) {
      const response = await cache.match(request);
      if (response) {
        const blob = await response.blob();
        totalSize += blob.size;
      }
    }
  }
  
  return totalSize;
}

// Vider le cache
async function clearCache() {
  const cacheNames = await caches.keys();
  
  return Promise.all(
    cacheNames.map((cacheName) => {
      if (cacheName !== STATIC_CACHE) {
        return caches.delete(cacheName);
      }
    })
  );
}

// Synchroniser les données hors ligne
async function syncOfflineData(data) {
  try {
    // Ici, vous enverriez les données au serveur
    const response = await fetch('/api/sync', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    
    if (response.ok) {
      // Notifier le client que la synchronisation est terminée
      const clients = await self.clients.matchAll();
      clients.forEach(client => {
        client.postMessage({
          type: 'SYNC_COMPLETE',
          payload: { success: true }
        });
      });
    }
  } catch (error) {
    console.log('Sync Error:', error);
    
    // Notifier le client de l'erreur
    const clients = await self.clients.matchAll();
    clients.forEach(client => {
      client.postMessage({
        type: 'SYNC_ERROR',
        payload: { error: error.message }
      });
    });
  }
}

// Gestion des notifications push
self.addEventListener('push', (event) => {
  if (!event.data) return;
  
  const data = event.data.json();
  const options = {
    body: data.body,
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/badge-72x72.png',
    vibrate: [200, 100, 200],
    data: data.data,
    actions: [
      {
        action: 'view',
        title: 'Voir',
        icon: '/static/icons/view-24x24.png'
      },
      {
        action: 'dismiss',
        title: 'Ignorer',
        icon: '/static/icons/dismiss-24x24.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Gestion des clics sur les notifications
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  const { action, data } = event;
  
  if (action === 'view') {
    // Ouvrir l'application à la page appropriée
    event.waitUntil(
      clients.openWindow(data.url || '/')
    );
  } else if (action === 'dismiss') {
    // Ne rien faire, la notification est déjà fermée
    return;
  } else {
    // Clic sur la notification elle-même
    event.waitUntil(
      clients.openWindow(data.url || '/')
    );
  }
});

// Synchronisation en arrière-plan
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

async function doBackgroundSync() {
  try {
    // Récupérer les données à synchroniser depuis IndexedDB
    const dataToSync = await getDataToSync();
    
    if (dataToSync.length > 0) {
      // Envoyer les données au serveur
      await syncDataToServer(dataToSync);
      
      // Nettoyer les données synchronisées
      await clearSyncedData();
    }
  } catch (error) {
    console.log('Background Sync Error:', error);
  }
}

async function getDataToSync() {
  // Ici, vous récupéreriez les données depuis IndexedDB
  return [];
}

async function syncDataToServer(data) {
  // Ici, vous enverriez les données au serveur
  return fetch('/api/sync', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
}

async function clearSyncedData() {
  // Ici, vous supprimeriez les données synchronisées d'IndexedDB
}
