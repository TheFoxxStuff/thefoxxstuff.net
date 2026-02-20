<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { auth } from '$lib/stores/auth.js';
  let users = $state([]);
  let loading = $state(true);
  const loadUsers = async () => { loading = true; try { users = await api.auth.users(); } catch (e) { console.error(e); } finally { loading = false; } };
  onMount(loadUsers);
  const updateRole = async (userId, role) => { try { await api.auth.updateRole(userId, role); loadUsers(); } catch (err) { alert(err.message); } };
  const deleteUser = async (userId) => { if (!confirm('Delete?')) return; try { await api.auth.deleteUser(userId); loadUsers(); } catch (err) { alert(err.message); } };
</script>
<svelte:head><title>Users Admin - TheFoxxStuff</title></svelte:head>
<div>
  <h1 class="font-display text-3xl tracking-wide mb-8">Users</h1>
  {#if loading}<div class="space-y-4">{#each Array(3) as _}<div class="h-16 bg-[--w8] rounded-xl animate-pulse"></div>{/each}</div>
  {:else}<div class="space-y-2">{#each users as user}
    <div class="card p-4 flex justify-between items-center">
      <div>
        <h3 class="font-medium flex items-center gap-2">
          {user.username}
          {#if user.role === 'admin'}<span class="px-2 py-0.5 text-xs bg-accent-green text-dark-950 rounded">ADMIN</span>{/if}
          {#if user._id === $auth.user?._id}<span class="text-[--w60] text-sm">(you)</span>{/if}
        </h3>
        <p class="text-sm text-[--w60]">{user.email} • Joined {new Date(user.created_at).toLocaleDateString()}</p>
      </div>
      {#if user._id !== $auth.user?._id}
        <div class="flex gap-2">
          <select onchange={(e) => updateRole(user._id, e.target.value)} value={user.role} class="input text-sm w-auto">
            <option value="user">User</option>
            <option value="admin">Admin</option>
          </select>
          <button onclick={() => deleteUser(user._id)} class="btn btn-danger text-sm">Delete</button>
        </div>
      {/if}
    </div>
  {/each}</div>{/if}
</div>
