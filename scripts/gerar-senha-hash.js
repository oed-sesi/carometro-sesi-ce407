#!/usr/bin/env node
/**
 * gerar-senha-hash.js
 * Gera o hash SHA-256 de uma senha para usar no data/config.json
 *
 * Uso:
 *   node scripts/gerar-senha-hash.js <sua-senha>
 *
 * Exemplo:
 *   node scripts/gerar-senha-hash.js minhaSenha123
 *
 * O hash gerado deve ser colado no campo "senha_hash" do usuário
 * no arquivo data/config.json
 */

const { createHash } = require('crypto');

const senha = process.argv[2];

if (!senha) {
  console.error('\n❌  Uso: node scripts/gerar-senha-hash.js <sua-senha>\n');
  process.exit(1);
}

const hash = createHash('sha256').update(senha).digest('hex');

console.log('\n─────────────────────────────────────────────────────');
console.log('  Carômetro Escolar — Gerador de Hash de Senha');
console.log('─────────────────────────────────────────────────────');
console.log(`  Senha informada : ${senha}`);
console.log(`  Hash SHA-256    : ${hash}`);
console.log('─────────────────────────────────────────────────────');
console.log('\n  Cole o hash acima no campo "senha_hash" do usuário');
console.log('  em data/config.json\n');
